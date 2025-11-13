
export interface Review {
    id: string;
    book_id: string;
    user_id: string;
    user_name: string;
    text: string;
    rating: number;
    added_date: string;
    is_liked_by_me: boolean; 
    likes_count: number;
}

export interface ReviewsList {
    reviews: Review[];
    total_count: number;
    page_number: number;
    page_size: number;
    total_pages: number;
}
