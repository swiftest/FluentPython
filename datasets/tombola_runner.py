import abc
import random
from random import randrange
import sys
import doctest
from random import shuffle


class Tombola(abc.ABC):
    
    @abc.abstractmethod
    def load(self, iterable):
        """从可迭代对象中添加元素"""
        
    @abc.abstractmethod
    def pick(self):
        """随即删除元素，然后将其返回。如果实例为空，这个方法应该抛出`LookupError`。"""
        
    def loaded(self):
        return bool(self.inspect())
    
    def inspect(self):
        """返回一个有序元组，由当前元素构成。"""
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)
        return tuple(sorted(items))


class BingoCage(Tombola):

    def __init__(self, items):
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)

    def load(self, items):
        self._items.extend(items)
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')

    def __call__(self):
        self.pick()


class LotteryBlower(Tombola):
    
    def __init__(self, iterable):
        self._balls = list(iterable)
        
    def load(self, iterable):
        self._balls.extend(iterable)
        
    def pick(self):
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError('pick from empty LotteryBlower')
        return self._balls.pop(position)
                               
    def loaded(self):
        return bool(self._balls)
                               
    def inspect(self):
        return tuple(sorted(self._balls))


@Tombola.register
class TomboList(list):
    
    def pick(self):
        if self:
            position = randrange(len(self))
            return self.pop(position)
        else:
            raise LookupError('pop from empty TomboList')
    
    load = list.extend
    
    def loaded(self):
        return bool(self)
    
    def inspect(self):
        return tuple(sorted(self))


class TumblingDrum(Tombola):

    def __init__(self, iterable):
        self._balls = []
        self.load(iterable)

    def load(self, iterable):
        self._balls.extend(iterable)
        shuffle(self._balls)

    def pick(self):
        return self._balls.pop()


TEST_FILE = 'tombola_tests.rst'
TEST_MSG = '{0:16} {1.attempted:2} tests, {1.failed:2} failed - {2}'


def main(argv):
    verbose = '-v' in argv
    real_subclasses = Tombola.__subclasses__()
    #virtual_subclasses = list(Tombola._abc_registry)
    for cls in real_subclasses + [TomboList]:
        test(cls, verbose)
        
        
def test(cls, verbose=False):
    res = doctest.testfile(TEST_FILE, globs={'ConcreteTombola': cls}, verbose=verbose, 
                           optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
    tag = 'FAIL' if res.failed else 'OK'
    print(TEST_MSG.format(cls.__name__, res, tag))
    
    
    
if __name__ == '__main__':
    main(sys.argv)
