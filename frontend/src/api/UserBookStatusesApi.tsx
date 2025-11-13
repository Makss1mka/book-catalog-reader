import { fetch_with_refresh } from "./CustomFetchs";
import { UserBookStatusList } from "../models/User";
import { Review } from "../models/Review";
import { Book } from "../models/Book";
import CommonResponse from "./CommonResponse";

export async function getUserBookStatusedBooks(
    status: string, pageNum: number = 0, pageSize: number = 20
): Promise<CommonResponse<UserBookStatusList | string> | undefined> {
    let url = "/api/book-service/books/user-status?status=" + status;

    url += `&page_size=${pageSize}&page_number=${pageNum}&`
    url += `sort_by=added_date&sort_order=desc`

    console.log(url);
    return await fetch_with_refresh(url);
} 


export async function addUserBookStatus(book: Book, status: string): Promise<CommonResponse<Review | string> | undefined> {
    let url = `/api/book-service/books/${book.id}/user-status`;

    return await fetch_with_refresh<Review>(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: status,
        })
    });
} 

export async function updateUserBookStatus(book: Book, new_status: string): Promise<CommonResponse<Review | string> | undefined> {
    let url = `/api/book-service/books/${book.id}/like`;

    return await fetch_with_refresh<Review>(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: new_status,
        })
    });
} 

export async function deleteUserBookStatus(book: Book): Promise<CommonResponse<string> | undefined> {
    let url = `/api/book-service/books/${book.id}/user-status`;

    return await fetch_with_refresh<string>(url, {
        method: 'DELETE'
    });
} 

export async function updateReadingEndPage(book: Book, new_end_page: number): Promise<CommonResponse<string> | undefined> {
    let url = `/api/book-service/books/${book.id}/user-status/end-page`;

    return await fetch_with_refresh<string>(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            end_page: new_end_page,
        })
    });
} 
