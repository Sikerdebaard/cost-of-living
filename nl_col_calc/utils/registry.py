import pandas as pd

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class CalcResultRegistry(metaclass=Singleton):
    _reg = {} 

    def rem(self, k):
        if k in self._reg:
            del self._reg[k]

    def get(self):
        if not self._reg or len(self._reg) == 0:
            return None

        res = {}
        for k, v in self._reg.items():
            if v[0] == 'add':
                res[k] = {'benefits': v[1], 'expenses': float('NaN')}
            else:
                res[k] = {'benefits': float('NaN'), 'expenses': v[1]}
        
        df = pd.DataFrame.from_dict(res, orient='index')[['benefits', 'expenses']]

        return df


    def add(self, name, value):
        self._reg[name] = ('add', value)

    def sub(self, name, value):
        self._reg[name] = ('sub', value)
