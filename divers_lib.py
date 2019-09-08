class Point:
    def __init__(self, id: int, x: float, y: float, time=360):
        self.x = x
        self.y = y
        self.id = id
        self.parent = None
        self.childs = []
        self.time = time
    
    

    def getTime(self, dest) -> float:
        return 10 + abs(dest.x - self.x) + abs(dest.y - self.y)
    
    def add_glob(self):
        i = 0
        b = True
        for child in self.childs:
            if isinstance(child, DropOff):
                b = False 

        while (i < len(self.parent.childs)):
            if (self != self.parent.childs[i] and not isinstance(self.parent.childs[i], Courier)):
                self.childs.append(self.parent.childs[i].copy())
                self.childs[-1].parent = self
                self.childs[-1].time=self.time+self.getTime(dest =  self.childs[-1])
                self.new_time_child()
                if (self.childs[-1].time < self.childs[-1].fromT):
                    self.childs[-1].time = self.childs[-1].fromT
                if isinstance(self.childs[-1], PickUp): 
                    i += self.childs[-1].check()
                else:
                    b = False
            i += 1
                #self.sons_time.append(self.getTime(source =  self,dest =  child))
        
        if b:
            now = self
            courier_use_id = []
            pickUp_use_id = []
            while (now != None):
                if isinstance(now, Courier):
                    courier_use_id.append(now.id)
                elif isinstance(now, PickUp):
                    pickUp_use_id.append(now.id)
                now = now.parent 
            for courier in couriers:
                if ((len(pickUps)-len(pickUp_use_id)) != 0 and courier.id not in courier_use_id):
                    self.childs.append(courier.copy()) 
                    self.childs[-1].parent = self    
        
        if len(self.childs) != 0: 
            for child in self.childs:
                child.add_glob()

    def new_time_child(self):
        for child in self.childs:
            child.time = self.time + self.getTime(child)
            if (child.time < child.fromT):
                child.time = child.fromT

class Courier(Point):
    
    def __init__(self, courier_id, location_x, location_y):
        super().__init__(courier_id, location_x, location_y)
        
    # def move(self, nextPoint: Point):
    #     """метод перемещения курьера"""
        
    #     self.time += self.getTime(nextPoint)
    #     self.x = nextPoint.x
    #     self.y = nextPoint.y
    
    def copy(self):
        """копирует объект курьера в дереве с точками доставки товаров, имеющихся на руках"""

        res = Courier(courier_id = self.id, location_x = self.x, location_y =  self.y)
        for child in self.childs:
            res.addClient(child.copy())
        return res

    def addClient(self, dropOff):
        """добавляет точки доставки к скопированному курьеру"""
        self.childs.append(dropOff)
        self.childs[-1].parent = self
        self.childs[-1].time=self.time+self.getTime(dest =  self.childs[-1])
        #self.sons_time.append(self.getTime(nextPoint =  self.childs[-1]))
        if (self.childs[-1].time < self.childs[-1].fromT):
            self.childs[-1].time = self.childs[-1].fromT

    def add_glob(self):
        now = self
        pickUp_use_id = []
        while (now != None):
            if isinstance(now, PickUp):
                pickUp_use_id.append(now.id)
            now = now.parent            
        ### globalnaya peremenaya PickUps
        for pickUp in pickUps:
            if (pickUp.id not in pickUp_use_id):
                self.childs.append(pickUp.copy())
                self.childs[-1].parent = self
                self.childs[-1].time=self.time+self.getTime(dest =  self.childs[-1])
                if (self.childs[-1].time < self.childs[-1].fromT):
                    self.childs[-1].time = self.childs[-1].fromT
        
        if len(self.childs) != 0: 
            for child in self.childs:
                child.add_glob()

          

class DropOff(Point):

    def __init__(self, dropOff_id, location_x, location_y, orderID, fromT, toT, payment):
        super().__init__(dropOff_id, location_x, location_y)
        self.orderID = orderID
        self.fromT = fromT
        self.toT = toT
        self.payment = payment
        self.courier_id = 0
    
    def copy(self):
        """копирует объект точки доставки"""
        res = DropOff(self.id, self.x, self.y, self.orderID, self.fromT, self.toT, self.payment)
        return res

    def add(self, parent):
        self.parent = parent
        for child in self.parent.childs:
            if self != child:
                self.childs.append(self.copy())
                self.childs[-1].time=self.time+self.getTime(dest =  self.childs[-1])
                #self.sons_time.append(self.getTime(source =  self,dest =  child))
                


class PickUp(Point):

    def __init__(self, pickUp_id, location_x, location_y, fromT, toT):
        super().__init__(pickUp_id, location_x, location_y)
        self.fromT = fromT
        self.toT = toT
        self.courier_id = 0

    def copy(self):
        """копирует объект точки взятия товара в дереве с точкой доставки"""
        res = PickUp(self.id, self.x, self.y, self.fromT, self.toT)
        res.addClient(self.childs[0].copy())
        return res

    def addClient(self, dropOff :DropOff):
        """добавляет точку доставки к скопированной точке взятия товара"""
        self.childs.append(dropOff)
        self.childs[-1].parent = self
        self.childs[-1].time=self.time+self.getTime(dest =  self.childs[-1])
        if (self.childs[-1].time < self.childs[-1].fromT):
            self.childs[-1].time = self.childs[-1].fromT
        #self.sons_time.append(self.getTime(nextPoint =  self.childs[-1]))

    def checkTime(self, dropOffs = []):
        """проверяет временные окна и конец рабочего дня. Строит все варианты маршрутов из dropOff и вызывает checkTimeSons"""
        
        for child in [*self.childs, *dropOffs]:
            child.add(self)

        return self.checkTimeSons()

    def checkTimeSons(self):
        """проверяет попадания в окно и при необходимости удаляет"""
        i = 0
        while (i < len(self.childs)):
            if (self.childs[i].time>self.childs[i].toT or self.childs[i]>1439):
                self.childs.remove(self.childs[i])
            else:
                if (len(self.childs[i].childs) != 0):
                    i += self.childs[i].checkTimeSons()
                i+=1

        if (len(self.childs) == 0):
            self.parent.childs.remove(self)
            return -1
        
        return 0

        
    def check(self):
        drop = []
        for child in self.parent.childs:
            if isinstance(child, DropOff):
                drop.append(child.copy())
        return self.checkTime(drop)


couriers = [Courier(0,0,0), Courier(1, 50, 50)]
dropOffs = [DropOff(0, 10, 0, 0, 400, 700, 50), DropOff(1, 80, 50, 1, 370, 700, 60)]#, DropOff(2, 90, 50, 2, 370, 700, 60)]
pickUps = [ PickUp(0, 5, 0, 380, 500), PickUp(1, 65, 50, 380, 500)]#, PickUp(2, 70, 50, 380, 500)]
pickUps[0].childs.append(dropOffs[0])
pickUps[1].childs.append(dropOffs[1])
#pickUps[2].childs.append(dropOffs[2])
dropOffs[0].parent = pickUps[0]
dropOffs[1].parent = pickUps[1]
#dropOffs[2].parent = pickUps[2]
    