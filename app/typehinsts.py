text:str = "ali"

def name(text:str | int) -> float: #float indicates return type,
    #str|int indicates incoming paramter type will be either int or str

    return 2.0 

digits: list[int] = [1,2,3,4,5]

table_5:tuple[int,...] = (1,2,3,4,5) #... indicates multiple value in tuples

shipment: dict[str,str|int] = { #key always str, values could be int or str only
    "ali":1,
    "mustafa":"ali"
}


#decorator function

def fence(func):
    def wrapper():
        print("*" * 10)
        func()
        print("*" * 10)
    return wrapper

@fence
def log():
    print("decorated")

log()