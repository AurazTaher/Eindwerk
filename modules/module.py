from abc import ABC,abstractmethod

class Module(ABC):
    def __init__(self,row_number,column_number,row_span,column_span):
        self.row = row_number
        self.column = column_number
        self.end_row = row_number + row_span
        self.end_column = column_number + column_span

    @abstractmethod
    def draw(self,image,start_x,start_y,end_x,end_y):
        pass

    