import Author from "./Author";

export interface Book {
    id: string;
    author_id: string;
    title: string;
    description: string;
    file_path: string;
    cover_path: string;
    genres: string[];
    added_date: string;
    status: string;
    total_rating: number;
    likes_count: number;
    pages_count: number;
    reviews_count: number;
    is_liked_by_me?: boolean
    author?: Author;
}

export interface BookSearch {
    books: Book[];
    total_count: number;
    page_number: number;
    page_size: number;
    total_pages: number;
}

export interface BookStatusUpdate {
    id: string;
    old_status: string;
    new_status: string;
    message: string;
}
