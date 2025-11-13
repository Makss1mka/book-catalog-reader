import { addLikeToBook, deleteLikeFromBook } from '../../api/BooksApi';
import { addReview, getAllBookReviews } from '../../api/ReviewApi';
import { IconLikeEmpty, IconLikeFilled } from '../../utils/icons';
import NotFoundPage from '../NotFoundPage/NotFoundPage';
import { ErrorPage, ErrorPageWithoutMessage } from '../ErrorPage/ErrorPage';
import ReviewCard from '../../utils/ReviewCard/ReviewCard';
import React, { useState, useEffect, useCallback } from 'react';
import { getBookById } from '../../api/BooksApi';
import { Review } from '../../models/Review';
import GlobalUser from '../../GlobalUser';
import { Book } from '../../models/Book';
import ReactDOM from 'react-dom/client';
import './BookPage.css';
import ReadingPage from '../ReadingPage/ReadingPage';


interface BookPageProps {
    book_id: string;
}

export default function BookPage({ book_id }: BookPageProps) {
    // BOOK
    const [book, setBook] = useState<Book | undefined>(undefined);
    const [rating, setRating] = useState<number>(0);
    const [genres, setGenres] = useState<string>("");
    const [isLikedByMe, setIsLikedByMe] = useState<boolean>(false);
    const [likesCount, setLikesCount] = useState<number>(0);

    // REVIEWS
    const [reviews, setReviews] = useState<Review[] | undefined>(undefined);
    const [reviewsPageNum, setReviewsPageNum] = useState<number>(1);
    const reviewsPageSize = 10;

    // REVIEW ERROR
    const [showErrOnAddReview, setShowErrOnAddReview] = useState<boolean>(false);
    const [addReviewErrText, setAddReviewErrText] = useState<string>("");

    // STATUSES
    const [isStatusMenuOpen, setIsStatusMenuOpen] = useState<boolean>(false);

    // COMMON ERRORS
    const [error, setError] = useState<string | null>(null);





    // GET BOOK
    useEffect(() => {
        const loadBook = async () => {
            const bookResp = await getBookById(book_id);

            if (bookResp === undefined || typeof bookResp.data === "string" || bookResp.data === null) {
                if (bookResp && typeof bookResp.data === "string") {
                     setError(bookResp.data);
                } else {
                     setError("NOT_FOUND");
                }
                return;
            }

            const loadedBook = bookResp.data as Book;

            console.log(`POPA ${loadedBook.is_liked_by_me}`)
            console.log(`POPA ${loadedBook.is_liked_by_me ?? false}`)

            setBook(loadedBook);
            setGenres(loadedBook.genres ? loadedBook.genres.join(", ") : "");
            setRating(Math.min(Math.max(Math.round(loadedBook.total_rating ?? -1), 0), 5));
            setIsLikedByMe(loadedBook.is_liked_by_me ?? false);
            setLikesCount(loadedBook.likes_count ?? 0);
        };

        loadBook();
    }, [book_id]);

    
    // GET REVIEWS
    const loadReviews = useCallback(async (page: number, append: boolean) => {
        if (!book) return;

        const reviewResp = await getAllBookReviews(book, page, reviewsPageSize);

        if (reviewResp === undefined) {
            setError("SERVER_ERROR");
            return;
        } else if (typeof reviewResp.data === "string") {
            setError(reviewResp.data);
            return;
        }

        const newReviews = reviewResp.data.reviews;

        if (newReviews.length > 0) {
            setReviews(prev => append ? [...(prev || []), ...newReviews] : newReviews);
            setReviewsPageNum(page);
        } else if (!append && newReviews.length === 0) {
             setReviews([]);
        }
    }, [book]);

    useEffect(() => {
        if (book && reviews === undefined) {
            loadReviews(reviewsPageNum, false);
        }
    }, [book, reviews, loadReviews, reviewsPageNum]);
    




    const handleLikeClick = async () => {
        if (GlobalUser.isEmpty() || book === undefined) return;

        if (isLikedByMe) {
            let response = await deleteLikeFromBook(book);

            if (response === undefined || response.status !== "success") {
                console.log(`Some error. ${response}.`);
                return;
            } else {
                setLikesCount(prev => prev - 1)
                setIsLikedByMe(false)
            }
        } else {
            let response = await addLikeToBook(book);

            if (response === undefined || response.status !== "success") {
                console.log(`Some error. ${response}.`);
                return;
            } else {
                setLikesCount(prev => prev + 1)
                setIsLikedByMe(true)
            }
        }
    };

    const handleReviewsLoad = async () => {
        if (book === undefined) return;

        let reviewResp = await getAllBookReviews(book, reviewsPageNum + 1, reviewsPageSize);

        if (reviewResp === undefined) return;
        if (typeof reviewResp.data === "string") {
            setError(reviewResp.data);   
            return;
        }

        let newReviews = reviewResp.data.reviews; 
        if (newReviews.length) {
            setReviews(prev => [...(prev || []), ...newReviews]);
            setReviewsPageNum(prev => prev + 1);
        }
    };

    const handleAddReview = async (event: React.FormEvent<HTMLFormElement>) => {
        if (book === undefined || GlobalUser.isEmpty()) return

        event.preventDefault();

        let ratingInput = (event.currentTarget.elements.namedItem("rating") as HTMLInputElement);

        let rating: number | undefined;
        if (!ratingInput || (rating = parseInt(ratingInput.value, 10)) === undefined || isNaN(rating)) {
            setShowErrOnAddReview(true);
            setAddReviewErrText("Выберите значение рейтинга.");
            return;
        }

        const textInput = (event.currentTarget.elements.namedItem("reviewText") as HTMLInputElement);
        const text = textInput ? textInput.value : "";

        console.log("Рейтинг отзыва:", rating);
        console.log("Текст отзыва:", text);

        let reviewResp = await addReview(text, rating, book);

        if (reviewResp === undefined || reviewResp.data === undefined) return;
        if (typeof reviewResp.data === "string") {
            setShowErrOnAddReview(true);  
            setError(reviewResp.data);
            return;
        }
        
        setReviews(prevReviews => {
            if (reviewResp === undefined || reviewResp.data === undefined) return prevReviews;

            let newReview = reviewResp.data;

            if (prevReviews === undefined || typeof newReview === "string") return prevReviews;

            let newReviews = [...prevReviews];
            newReviews.unshift(newReview);
            return newReviews;
        });
    };

    const handleStartReadingPressed = async () => {
        if (book === undefined) return;
    
        let main = document.getElementById('main');

        if (!main) return;

        ReactDOM.createRoot(main).render(
            <ReadingPage book_id={ book.id } />
        );
    }



    if (error) {
        if (error === "NOT_FOUND") {
            return <NotFoundPage />;
        }
        if (error === "SERVER_ERROR") {
             return <ErrorPageWithoutMessage />;
        }
        return <ErrorPage message={error} />;
    }

    if (!book || !reviews) {
        return <div className="BookPage">Loading...</div>;
    }

    // const statusMenu = [
    //     { key: "1", label: "Читаю", onclick={ handleReadingStatusClicked } },
    //     { key: "2", label: "Прочитал", onclick={ handleReadStatusClicked } },
    //     { key: "3", label: "Бросил читать", onclick={ handleDropStatusClicked } },
    // ];

    // <Dropdown menu={{ items: statusMenu }} trigger={['click']}>
    //                 <Button>
    //                     {userStatus == "" 
    //                         ? <IconFavouriteEmpty className='BookPage_UpperBlock_StatusIcon'/>
    //                         : <IconFavouriteFilled className='BookPage_UpperBlock_StatusIcon'/>
    //                     }
    //                 </Button>
    //             </Dropdown>

    // <p className='BookPage_RatingsCount'>{book.r}</p>
    console.log(isLikedByMe)

    
    return (
        <div className="BookPage">
            <div className="BookPage_LeftUpperPannel">
                {
                    (book.cover_path === undefined) 
                    ? undefined 
                    : <img className="BookCard_cover" src={ book.cover_path } alt="Book cover"></img>
                }
            </div>

            <div className="BookPage_RigthUpperPannel">
                <div className="BookPage_UpperBlock">
                    <label className='BookPage_NameLabel'>{book.title}</label>
                </div>
                {
                    (book.author)
                        ? <p className='BookPage_Author'>{book.author.name}</p>
                        : <></>
                }
                <p className='BookPage_Rating'>
                    {'★'.repeat(rating)}
                    {'☆'.repeat(5 - rating)}
                    {` ${rating.toFixed(2)}/5.0`}
                </p>
                <p className='BookPage_Genres'>{genres}</p>
                <div className='BookPage_LikeBlock'>
                    <p className='BookPage_Likes'>{likesCount}</p>
                    <button
                        className="BookPage_LikeButton"
                        onClick={ handleLikeClick }
                    >
                        {isLikedByMe
                            ? <IconLikeFilled className="BookPage_LikeButtonIcon_Active" />
                            : <IconLikeEmpty className="BookPage_LikeButtonIcon_Inactive" />
                        }
                    </button>
                </div>
                <button className="BookPage_StartReading" onClick={ handleStartReadingPressed }>
                    Go read
                </button>
            </div>


            <div className='BookPage_ReviewCreateForm'>
                <form onSubmit={handleAddReview}>
                    <div className='BookPage_ReviewCreateForm_RatingSelector'>
                        <p>Выберите рейтинг:</p>
                        {[1, 2, 3, 4, 5].map(star => (
                            <label key={star}>
                                <input
                                    type="radio"
                                    name="rating"
                                    value={star}
                                />
                                {'★'.repeat(star)}
                            </label>
                        ))}
                    </div>
                    <textarea
                        className='BookPage_ReviewCreateForm_TextInput'
                        name="reviewText"
                        placeholder="Write your review"
                    />
                    <div >
                        {
                            showErrOnAddReview && (
                                <p className="BookPage_InvalidData" id="BookPage_InvalidData">{ addReviewErrText }</p>
                            )
                        }
                    </div>
                    
                    <button type="submit">Add</button>
                </form>
            </div>
            <div className='BookPage_ReviewsList'>
                {
                    reviews.map((review) => (
                        <ReviewCard
                            review={review}
                            key={review.id}
                        />
                    ))
                }
                <button onClick={ handleReviewsLoad }>More...</button>
            </div>
        </div>
    );
}

