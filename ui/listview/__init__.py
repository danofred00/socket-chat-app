#coding:UTF-8

from typing import Any, Iterable, Mapping
from tkinter import Widget, Pack, XView, YView, Frame

class Observer:

    def update(self, object :Any):
        raise NotImplementedError("")

class Observable:

    def __init__(self) -> None:
        self._observers : list[Observer] = []
    
    @property
    def observers(self):
        return self._observers
    
    def add_observer(self, observer :Observer):
        self.observers.append(observer)
    
    def remove_observer(self, o:Observer):
        self.observers.remove(o)

    def update_observers(self, object):
        for obs in self.observers:
            obs.update(object)


class ListModel(Observable):
    
    def __init__(self, model = []) -> None:
        
        self._model : list = model
        self._observers = []
        
    
    def add(self, item: Any) -> None:
        self._model.insert(-1, item)

    def insert(self, index :int, item) -> None:
        self._model.insert(index, item)
        # notify observers
        self.update_observers(self)
    
    def remove(self, index :int) -> None:
        if index >= len(self._model):
            raise IndexError()
        
        del self._model[index]
        # notify observer
        self.update_observers(self)
    
    def get(self, index :int):
        return self._model[index]
    

class ListItemDelegate(Frame):

    def __init__(self, master, object) -> None:
        super().__init__(master)
        self.item = object
        #self.master = master

    def delegate(self) -> Widget :
        raise NotImplementedError("")
    
    def pack(self) -> None:
        self.delegate().pack()
        super().pack()


class ListView(Frame, Observer, Pack, XView, YView):

    def __init__(self, master, model :ListModel) -> None:
        super().__init__(master)
    
        self._model : ListModel = model
        self._delegate = None

        self.content = self
        self._setup_model()
    
    @property
    def model(self) :
        return self._model
    
    def set_model(self, model : ListModel):
        self._model = model
    
    @property
    def delegate(self):
        return self._delegate
    
    def set_delegate(self, delegate :Widget):
        self._delegate = delegate

    def _setup_model(self):
        self._model.add_observer(self)
    
    def update(self, object) -> None:
        self.set_model(object)

    def _show_items(self):

        for elt in self._model._model:
            
            print(elt)
            item = self.delegate(self.content, elt)
            item.pack()
    
    def pack(self):
        self._show_items()
        super().pack()