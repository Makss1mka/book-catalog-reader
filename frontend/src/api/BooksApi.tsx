import { fetch_with_refresh } from "./CustomFetchs";
import CommonResponse from "./CommonResponse";
import { BookSearch, Book } from "../models/Book";

export async function getAllBooks(
    keyWords: string | null = null, 
    genres: string | null = null, 
    pageNum: number = 0, 
    pageSize: number = 20
): Promise<CommonResponse<BookSearch | string> | undefined> {
    let url = "/api/book-service/books/search?";

    if (keyWords) url += `key=${keyWords}&`;
    if (genres) url += `book_genres=${genres}&`;

    url += `page_size=${pageSize}&page_number=${pageNum}&`
    url += `sort_by=rating&sort_order=desc&`

    console.log(url);

    return await fetch_with_refresh<BookSearch>(url);
} 

export async function getBookById(book_id: string): Promise<CommonResponse<Book | string> | undefined> {
    let url = `/api/book-service/books/${book_id}`;

    return await fetch_with_refresh<Book>(url);
} 

export async function addLikeToBook(book: Book): Promise<CommonResponse<string> | undefined> {
    let url = `/api/book-service/books/${book.id}/likes`;

    return await fetch_with_refresh<string>(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            bookId: book.id,
        })
    });
} 

export async function deleteLikeFromBook(book: Book): Promise<CommonResponse<string> | undefined> {
    let url = `/api/book-service/books/${book.id}/likes`;

    return await fetch_with_refresh<string>(url, {
        method: 'DELETE'
    });
} 


