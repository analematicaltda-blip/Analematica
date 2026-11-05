export interface Amenity {
    id: string;
    name: string;
    icon?: string;
}

export interface RoomType {
    id: string;
    name: string;
    capacity: number;
    base_price: number;
    amenities: Amenity[];
}

export interface Room {
    id: string;
    room_number: string;
    room_type: RoomType;
    status: 'AVAILABLE' | 'OCCUPIED' | 'MAINTENANCE';
    housekeeping_status: 'CLEAN' | 'DIRTY' | 'IN_PROGRESS';
}
