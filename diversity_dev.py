from divers_lib import Point, DropOff, PickUp, Courier, couriers

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

def test(point):
    if point not in test_:
        test_.append(point)
    else:
        print(point)
    for child in point.childs:
        test(child)
test_ = []

test(couriers[0])

min_point = optimalRoute(weightsAr =  [0] , points =  [couriers[0]])
print("111")

