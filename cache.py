import json
import atexit
from cachetools import LRUCache

class Cache:
    def __init__(self):
        self._cache = LRUCache(1000)
        self._try_load()
        atexit.register(self.save)
    
    def _try_load(self):
        try:
            with open('cache.json', 'r') as f:
                cache_dict = json.load(f)
                self._cache.update(cache_dict)
        except FileNotFoundError:
            pass
    
    def save(self):
        cache_dict = dict(self._cache)  
        with open('cache.json', 'w') as f:
            json.dump(cache_dict, f)
    
    def has(self, key: str) -> bool:
        return key in self._cache
    
    def add(self, key: str):
        self._cache[key] = True
