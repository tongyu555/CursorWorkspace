class Person1 :
        def __init__(self,name,age,id):
            self.name = name
            self._age = age
            self.__id = id

        # get 方法
        @property
        def age(self):
            return self._age

        @property
        def id(self):
            return self.__id

        # set 方法
        @age.setter
        def age(self,value):
            if value <= 120 :
                self.age = value
            else :
                self.age = 120

        @id.setter
        def id(self,value):
            self.id = value

        def show(self):
            print(self.name + "age : " + str(self._age) + "id : " + str(self.__id))

class Person2:
    def __init__(self,name,age,id):
        self.name = name
        self.age = age
        self.id = id

p1 = Person1("jim",28,143243232323)
print(p1.age)
p1._age = 29
print(p1.age)

p2 = Person2("bob",30,18293738738)
print(p2.age)
p2.age = 31
print(p2.age)


