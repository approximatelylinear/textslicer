
#   Stdlib
import os
import datetime
import csv
import traceback
import pdb
from pprint import pformat

#   3rd party
from termcolor import colored

#   Custom
from ..base.tokenize import update_segments


class CharFilter(object):
    def __init__(self, *args, **params):
        super(CharFilter, self).__init__()

    def process_item(self, text, **kwargs):
        raise NotImplementedError

    def finalize(self):
        pass

    def __call__(self, doc, **kwargs):
        field_in = kwargs.get('field_in')  or 'current'
        field_out = kwargs.get('field_out')  or 'current'
        segments = doc['text'][field_in]
        #   Precondition
        assert hasattr(segments, '__iter__')
        segments_ = []
        s_new = 0
        for segment in segments:
            #   Ignore the original boundaries, because we are (likely)
            #   changing the overall text length.
            text = segment['text']
            result = self.process_item(text, **kwargs)
            #   Modify the original boundaries
            e_new = len(result) + s_new
            segment['pos'] = (s_new, e_new)
            segment['text'] = result
            s_new = e_new
            segments_.append(segment)
        doc['text'][field_out] = segments_
        return doc


class Tokenizer(object):
    tokenizer_key = None
    tokenizer_name = None

    def __init__(self, *args, **kwargs):
        super(Tokenizer, self).__init__()

    def finalize(self):
        pass

    @staticmethod
    def tokenizer_matcher(text):
        raise NotImplementedError

    def process(self, doc, **params):
        #   !!!!!!!!!!!!!!!!!!!!!!!!
        assert 'text' in doc
        #   !!!!!!!!!!!!!!!!!!!!!!!!
        field_in = params.get('field_in')  or 'current'
        field_out = params.get('field_out')  or 'current'
        tokens = doc['text'].setdefault('tokens', {})
        segments = doc['text'][field_in]
        try:
            segments_, targets_ = update_segments(
                segments, self.tokenizer_matcher
            )
        except Exception as e:
            print e
            print colored(traceback.format_exc(), 'red')
            # pdb.set_trace()
        if segments_:
            doc['text'][field_out] = segments_
        if self.tokenizer_key:
            tokens_new = tokens.setdefault(self.tokenizer_key, [])
            tokens_new.extend(targets_)
            if self.tokenizer_name:
                for t in tokens_new:
                    t['name'] = self.tokenizer_name
        return doc

    def __call__(self, doc, **params):
        return self.process(doc, **params)


class TokenFilter(object):
    type_ = None

    def __init__(self, *args, **kwargs):
        super(TokenFilter, self).__init__()

    def finalize(self):
        pass

    def process(self, doc, **params):
        field_in = params.get('field_in')  or 'current'
        field_out = params.get('field_out')  or 'current'
        segments = doc['text'][field_in]
        #   Remove all elements with a (previously identified) type of <type_>
        type_ = self.type_
        segments_out = [ seg for seg in segments if seg['name'] != type_ ]
        doc['text'][field_out] = segments_out
        return doc

    def __call__(self, doc, **params):
        return self.process(doc, **params)


class Filter(object):
    type_ = None
    key = None

    def __init__(self, **params):
        self.ct_total = 0.0
        self.ct = 0.0
        self.pr = 1.0
        self.set_path_out(**params)

    def set_path_out(self, **params):
        path_out = params.get('path_out')
        if not path_out:
            #   e.g. '20130306-00-00'
            today = datetime.datetime.today().strftime('%Y%m%d-%H-%M')
            path_base = params.get('path_base') or '.'
            path_out = os.path.join(path_base, 'filter')
            if self.type_:
                path_out = os.path.join(path_out, self.type_)
            if not os.path.exists(path_out):
                os.makedirs(path_out)
            path_out = os.path.join(path_out, today + '.csv')
        else:
            base, _ = os.path.splitext(path_out)
            path_out = base + '.csv'
        self.path_out = path_out

    def finalize(self):
        ct_total, ct, pr = self.get_stats()
        with open(self.path_out, 'wb') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(
                ['total', 'ct_{0}'.format(self.key), 'pr_{0}'.format(self.key)]
            )
            writer.writerow([ct_total, ct, pr])

    def process(self, doc, **params):
        meta = doc.get('__meta__') or {}
        fltrs = set(meta.get('filters') or [])
        self.ct_total += 1
        if self.key in fltrs:
            self.ct += 1
            meta['skip'] = True
        elif meta.get(self.key):
            self.ct += 1
            fltrs.add(self.key)
            meta['skip'] = True
        meta['filters'] = list(fltrs)
        doc['__meta__'] = meta
        return doc

    def get_stats(self):
        try:
            self.pr = self.ct / self.ct_total
        except ZeroDivisionError:
            self.pr = 0.0
        return self.ct_total, self.ct, self.pr

    def __call__(self, doc, **params):
        return self.process(doc, **params)
