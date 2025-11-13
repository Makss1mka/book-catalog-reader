
export default interface Author {
    id: string;
    name: string;
    rating: number;
    common_genres: string[];
    books_count: number;
    reviews_count: number;
    likes_count: number;
    status: string;
}

export interface AuthorSearch {
    authors: Author[];
    total_count: number;
    page_number: number;
    page_size: number;
    total_pages: number;
}
