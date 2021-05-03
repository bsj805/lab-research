import threading

class sdict(): # dict with semaphore
    
    def __init__(self, iterable=dict()):
        # s는 semaphore
        self.d = iterable
        self.s = threading.BoundedSemaphore(1) # s의 초기값 1, 항상 0 <= s <= 1

    def __setitem__(self, key, val):
        self.s.acquire() # s가 1만큼 감소
        self.d[key] = val
        self.s.release() # s가 1만큼 증가
    
    def __getitem__(self, key):
        return self.d[key]
    
    def __delitem__(self, key):
        del self.d[key]
    
    def __str__(self):
        return str(self.d)

    def __len__(self):
        return len(self.d)
    
    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()

sd = sdict()
sd['a'] = 1
sd['b'] = 2
print(sd)
print(sd['a'])
print(len(sd))
del sd['a']
print(sd)
sd['c']=3
for idx,key in enumerate(sd.values()):
    print(idx,key)
print(sd.values()[0])
