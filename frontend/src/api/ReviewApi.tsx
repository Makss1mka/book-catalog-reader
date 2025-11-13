import { Review, ReviewsList } from "../models/Review";
import { fetch_with_refresh } from "./CustomFetchs";
import { Book } from "../models/Book";
import CommonResponse from "./CommonResponse";

export async function getAllBookReviews(book: Book, pageNum: number, pageSize: number): Promise<CommonResponse<ReviewsList | string> | undefined> {
    let url = `/api/review-service/reviews/${book.id}?page_size=${pageSize}&page_number=${pageNum}`;

    return await fetch_with_refresh<ReviewsList>(url);
} 


export async function addReview(text: string, rating: number, book: Book): Promise<CommonResponse<Review | string> | undefined> {
    let url = "/api/review-service/reviews/";
    
    return await fetch_with_refresh<Review>(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            book_id: book.id,
            text: text,
            rating: rating
        })
    });
}

export async function addLikeToReview(review: Review): Promise<CommonResponse<string> | undefined> {
    let url = `/api/review-service/reviews/likes/${review.id}`;
    
    return await fetch_with_refresh<string>(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
}


export async function deleteReview(review: Review): Promise<CommonResponse<Review | string> | undefined> {
    let url = `/api/review-service/reviews/${review.id}`;
    
    return await fetch_with_refresh<string>(url, {
        method: 'DELETE',
    });
}

export async function deleteLikeFromReview(review: Review): Promise<CommonResponse<string> | undefined> {
    let url = `/api/review-service/reviews/likes/${review.id}`
    
    return await fetch_with_refresh<string>(url, {
        method: 'DELETE',
    });
}


export async function updateReview(text: string | null = null, rating: number | null = null, review: Review): Promise<CommonResponse<Review | string> | undefined> {
    let url = `/api/review-service/reviews/${review.id}`;
    let body;

    if (text && !rating) body = { "text": text }
    if (!text && rating) body = { "rating": rating }
    if (text && rating) body = { "text": text, "rating": rating }

    return await fetch_with_refresh(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
    });
}
