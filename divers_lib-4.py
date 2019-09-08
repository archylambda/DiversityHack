import json
import requests
import sys
import os

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

    def __init__(self, pickUp_id, location_x, location_y,orderID, fromT, toT):
        super().__init__(pickUp_id, location_x, location_y)
        self.fromT = fromT
        self.toT = toT
        self.courier_id = 0
        self.orderID = orderID

    def copy(self):
        """копирует объект точки взятия товара в дереве с точкой доставки"""
        res = PickUp(self.id, self.x, self.y,self.orderID, self.fromT, self.toT)
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
            if (self.childs[i].time>self.childs[i].toT or self.childs[i].time>1439):
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



# couriers = [Courier(0,0,0), Courier(1, 50, 50)]
# dropOffs = [DropOff(0, 10, 0, 0, 400, 700, 50), DropOff(1, 80, 50, 1, 370, 700, 60)]#, DropOff(2, 90, 50, 2, 370, 700, 60)]
# pickUps = [ PickUp(0, 5, 0,0, 380, 500), PickUp(1, 65, 50,1, 380, 500)]#, PickUp(2, 70, 50, 380, 500)]
# pickUps[0].childs.append(dropOffs[0])
# pickUps[1].childs.append(dropOffs[1])
# #pickUps[2].childs.append(dropOffs[2])
# dropOffs[0].parent = pickUps[0]
# dropOffs[1].parent = pickUps[1]
# #dropOffs[2].parent = pickUps[2]

##
# v:
### read_from_url
dic_coord = []
response = requests.get("https://raw.githubusercontent.com/dostavista/phystech/master/data/contest_input.json")
data = json.loads(response.text)

### read_from_file__:::__
def read_input():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = app_dir + '/input.json'
    with open(input_file, 'r') as f:
            input_file = json.load(f)
    return input_file
def write_output(data_rec):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = app_dir + '/output.json'
    with open(output_file, 'w') as out_file:
           json.dump(data_rec, out_file)
if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
else:
    in_file = read_input()
    #write_output()
couriers_js = in_file['couriers']
depots = in_file['depots']
orders = in_file['orders']
# M:
def jsonToClass(jsonObject):
    dic_temp = {}
    coord = []
    for i in range(len(jsonObject)):
        temp_id = jsonObject[i]
        temp_x = temp_id['location_x']
        temp_y = temp_id['location_y']
        coord.append(temp_x)
        coord.append(temp_y)
        if jsonObject == couriers_js:
            dic_temp[temp_id['courier_id']] = coord
        else:
            dic_temp[temp_id['point_id']] = coord
        coord = []
    return dic_temp
# o: courier dict
dict_couriers = jsonToClass(couriers_js)
# o: depots dict
#dict_depots = jsonToClass(depots)
# M: class init
def initClass(input_dict):
    objectInit = []
    for key in input_dict:
        coord = input_dict[key]
        len_coord = len(coord)
        for i in range(len_coord-1):
            if input_dict == dict_couriers:
                objectInit.append(Courier(key,coord[i],coord[i+1]))
           # elif input_dict == dict_depots:
           #     objectInit.append(Depot(key,coord[i],coord[i+1]))
    return objectInit
# o: courier
#couriers = initClass(dict_couriers)            
# o: depots
#depots_object = initClass(dict_depots) 
# M
def jsonToClassOrder(jsonObject):
    dic_temp = []
    lst = []
    for i in range(len(jsonObject)):
        temp_id = jsonObject[i]
        lst.append(temp_id['order_id']) # 0
        lst.append(temp_id['pickup_point_id']) # 1
        lst.append(temp_id['pickup_location_x']) # 2
        lst.append(temp_id['pickup_location_y']) # 3
        lst.append(temp_id['pickup_from']) # 4
        lst.append(temp_id['pickup_to']) # 5
        lst.append(temp_id['dropoff_point_id']) # 6
        lst.append(temp_id['dropoff_location_x']) # 7
        lst.append(temp_id['dropoff_location_y']) # 8
        lst.append(temp_id['dropoff_from']) # 9
        lst.append(temp_id['dropoff_to']) # 10
        lst.append(temp_id['payment']) # 11
        dic_temp.append(lst)
        lst = []
    return dic_temp
order_obj = jsonToClassOrder(orders)
def initClassWithOrders(input_obj,class_type):
    objectInit = []
    index_order_obj = len(input_obj)
    for i in range(index_order_obj):
        a_lst = input_obj[i]
        j = 0
        if class_type == "DropOff":
            objectInit.append(DropOff(a_lst[j+6],a_lst[j+7],a_lst[j+8],a_lst[j],a_lst[j+9],a_lst[j+10],a_lst[j+11]))
        elif class_type == "PickUp":
            objectInit.append(PickUp(a_lst[j+1],a_lst[j+2],a_lst[j+3],a_lst[j+0],a_lst[j+4],a_lst[j+5]))
    
    return objectInit
# o
dropOffs = initClassWithOrders(order_obj,'DropOff')
# o
pickUps = initClassWithOrders(order_obj,'PickUp')
# o
couriers = initClass(dict_couriers)    
print(couriers[1].id,couriers[1].x,couriers[1].y)
# def __init__(self, dropOff_id, location_x, location_y, orderID, fromT, toT, payment):
print(dropOffs[1].id,dropOffs[1].x,dropOffs[1].y,dropOffs[1].orderID,dropOffs[1].fromT,dropOffs[1].toT,dropOffs[1].payment)
# self, pickUp_id, location_x, location_y,orderID, fromT, toT
print(pickUps[1].id,pickUps[1].x,pickUps[1].y,pickUps[1].orderID,pickUps[1].fromT,pickUps[1].toT)
for  i in range(len(dropOffs)):
   dropOffs[i].parent = pickUps[i]
   pickUps[i].childs.append(dropOffs[i])        
# o: depots
#depots_object = initClass(dict_depots) 
###
##
def optimalRoute(weightsAr: [float], points):
    weightsArr = weightsAr.copy()
    #points = []
    # for point in points1:
    #     points.append(point.copy())
    min_w = weightsArr[0]
    min_id = 0
    for i in range(1, len(weightsArr)):
        if (weightsArr[i] < min_w):
            min_w = weightsArr[i]
            min_id = i
        
    min_point = points[min_id]
    if len(min_point.childs) != 0:
        weightsArr.pop(min_id)
        points.pop(min_id)
       
        for i in range(len(min_point.childs)):
             weightsArr.append(min_point.childs[i].time)
             points.append(min_point.childs[i])
        
        min_point = optimalRoute(weightsAr =  weightsArr, points =  points)
    
    return min_point


couriers[0].add_glob()

min_point = optimalRoute(weightsAr =  [0] , points =  [couriers[0]])
####
p = min_point
temp_list = []

rez = []
while (p != None):
    if isinstance(p,Courier):
        temp_list.reverse
        for k in temp_list:
            data_w = {}
            data_w['courier_id'] = p.id
            data_w['order_id'] = k.orderID 
            if isinstance(k,DropOff):
                data_w['action'] = 'dropoff'
            else:
                data_w['action'] = 'pickup'
            data_w['point_id'] = k.id
            rez.append(data_w)
        temp_list = []
    else:
        temp_list.append(p)
    p = p.parent
write_output(rez)