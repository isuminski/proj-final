
class TestClass:
    def __init__(self, double=False):
        if double != 'True':
            self.type = 'Single'
            self.populate_123()
        else:
            self.type = 'Double'
            self.populate_123()
    
    
    def populate_123(self):
        if self.type == 'Double':
            self.one = 'two'
            self.two = 'four'
            self.three = 'six'
        else:
            self.one = 'one'
            self.two = 'three'
            self.three = 'five'
        pass
    
    def print_info(self):
        print(self.type)
        print(self.one, self.two, self.three)
        pass
    
    
statement = ''
while statement != 'exit':
    TestObject = TestClass(statement)
    TestObject.print_info()
    statement = input('try something! ')

    
            