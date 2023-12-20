class Room:

    def __init__(self, room_id : str, room_number : int) -> None:
    
        self.room_id = room_id
        self.room_number = room_number

    def get_room_id(self) -> str:
        return self.room_id

    def get_room_number(self) -> int:
        return self.room_number

