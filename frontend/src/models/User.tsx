
export default interface User {
    id: string;
    username: string;
    email: string;
    created_at: string;
    profile_picture: string;
}

export interface UserBookStatus {
    book_id: string;
    status: string;
    author_id: string;
    author_name: string;
    title: string;
    end_page: number;
}

export interface UserBookStatusList {
    books: UserBookStatus[];
    total_count: number;
    page_number: number;
    page_size: number;
    total_pages: number;
}

export interface UserLogin {
    access_token: string;
    refresh_token: string;
    user_data: User;
}

export interface AccessToken {
    access_token: string;
}

export interface UserSystemStatusUpdate {
    id: string;
    old_status: string;
    new_status: string;
    message: string
}

