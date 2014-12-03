import sqlite3 
import datetime
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import unittest

class Cache:
    def __init__(self, config):
        pass
    def keys(self):
        ''' Generator yielding all keys present'''
        raise NotImplementedError
    def add(self, funcname, code_hash, callgraph, 
            args, kwargs, return_values,
            runtime=datetime.datetime.now(), runningtime = None):
        ''' Cache function 'funcname' with the given code_hash, callgraph, arguments/keyword arguments
        and resulting return_values as well as the time it was called.
        (fname+args+kwargs) are used as primary key. 
        A change in code_hash indicates that the old value stored has to be invalidated.
        
        A previous entry with the same funcname but different code_hash or a change in '''
        raise NotImplementedError
    def delete(self):
        raise NotImplementedError
    def compare(self, funcname):
        ''' Check for presence of cached value for given parameters.
        :param funcname:
        :return: None if not present, else returns 'return_values' from funcname with fitting arguments.
        '''
        return None
    def invalidate(self):
        ''' Invalidate the complete cache. '''
        raise NotImplementedError


class SqliteCache(Cache):
    def __init__(self, config):
        self.connection = sqlite3.connect(config.file)
        c = self.connection.cursor()
        
        c.execute()


class PickleCache(Cache):
    def __init__(self, config):
        self.picklepath = None # Needed in case config['file'] fails.
        self.picklepath = config['file']
        if os.path.exists(self.picklepath):
            self.data = pickle.load(open(self.picklepath, 'rb'))
        else:
            self.data = dict()
    def add(self, funcname, code_hash, callgraph,
            args, kwargs, return_values,
            runtime=datetime.datetime.now(), runningtime = None):
        args_hash = hash((args, kwargs))
        if funcname not in self.data:
            self.data[funcname] = {}
        self.data[funcname][args_hash] = {'hash': code_hash, 'callgraph': callgraph,
                               'args': args, 'kwargs': kwargs, 'return_values': return_values,
                               'when': runtime, 'howlong': runningtime}

    def save(self):
        with open(self.picklepath, 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        

    def __del__(self):
        # TODO: __del__ parent
        try:
            self.save()
        except:
            print("Could not save cache!")

class TestPickleCache(unittest.TestCase):
    def setUp(self):
        fname = 'cache.pickle'
        if os.path.exists(fname):
            os.remove(fname)
        config = {'file': fname}
        self.return_values = 5
        self.uut = PickleCache(config)
        self.uut.add(funcname='myfunc', code_hash=123, callgraph=None, 
                args=None, kwargs=None, return_values = self.return_values)
        
    def tearDown(self):
        #del self.uut
        pass
    def test_compare_code_hash(self):
        self.assertEqual(self.return_values, self.uut.compare(funcname='myfunc', code_hash=123, ))
        self.assertNone(self.uut.compare(funcname='myfunc', code_hash=124))
    def test_compare_funcname(self):
        self.assertEqual(self.return_values, self.uut.compare(funcname='myfunc'))
        self.assertNone(self.uut.compare(funcname='notmyfunc'))
    def test_callgraph_changed(self):
        '''One of the functions in the callgraph has a changed hash'''
        self.uut.compare()
    def test_load_from_disk(self):
        config = {'file': self.uut.picklepath}
        del self.uut
        new_cache = PickleCache(config)
        self.assertEqual(self.return_values, new_cache.compare(funcname='myfunc', code_hash=123))
        self.uut = new_cache
    
    
    
if __name__=='__main__':
    unittest.main()
    