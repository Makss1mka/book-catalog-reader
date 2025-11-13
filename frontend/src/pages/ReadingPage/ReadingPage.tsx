import { ErrorPage, ErrorPageWithoutMessage } from '../ErrorPage/ErrorPage';
import NotFoundPage from '../NotFoundPage/NotFoundPage';
import { getBookById } from '../../api/BooksApi';
import { useEffect, useState } from 'react';
import { Book } from '../../models/Book';
import './ReadingPage.css';
import { updateReadingEndPage } from '../../api/UserBookStatusesApi';

interface ReadingPageProps {
    book_id: string;
    initial_page?: number;
}

export default function ReadingPage({ book_id, initial_page = 1 }: ReadingPageProps) {
    const [book, setBook] = useState<Book | undefined>(undefined);
    const [currentPage, setCurrentPage] = useState<number>(initial_page);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const imageUrl = `/api/book-service/books/${book_id}/page/${currentPage}`;
    const [error, setError] = useState<string | null>(null);

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

            setBook(loadedBook);
        };

        loadBook();
    }, [book_id]);



    if (error) {
        if (error === "NOT_FOUND") {
            return <NotFoundPage />;
        }
        if (error === "SERVER_ERROR") {
             return <ErrorPageWithoutMessage />;
        }
        return <ErrorPage message={error} />;
    }

    if (!book) {
        return <div className="ReadingPage">Loading...</div>;
    }


    const handleNextPage = async () => {
        if (currentPage < book.pages_count) {
            setIsLoading(true);
            setCurrentPage(prev => prev + 1);
            await updateReadingEndPage(book, currentPage);
        }
    };

    const handlePrevPage = async () => {
        if (currentPage > 1) {
            setIsLoading(true);
            setCurrentPage(prev => prev - 1);
            await updateReadingEndPage(book, currentPage);
        }
    };

    const isPrevDisabled = currentPage <= 1;
    const isNextDisabled = currentPage >= book.pages_count;

    return (
        <div className="ReadingPage">
            <div className="ReadingPage_Header">
                <p className="ReadingPage_PageIndicator">
                    Page {currentPage} / {book.pages_count}
                </p>
            </div>

            <div className="ReadingPage_Viewer">
                {isLoading && (
                    <div className="ReadingPage_Loading">
                        <span>Загрузка страницы...</span>
                    </div>
                )}
                <img 
                    className={`ReadingPage_Image ${isLoading ? 'loading' : 'loaded'}`}
                    src={imageUrl} 
                    alt={`Page ${currentPage} of ${book_id} - ${book.title}`}
                    onLoad={() => setIsLoading(false)} 
                />
            </div>

            <div className="ReadingPage_Controls">
                <button 
                    className="ReadingPage_Button" 
                    onClick={ handlePrevPage }
                    disabled={ isPrevDisabled } 
                >
                    Back
                </button>
                
                <button 
                    className="ReadingPage_Button" 
                    onClick={ handleNextPage } 
                    disabled={ isNextDisabled }
                >
                    Next
                </button>
            </div>
        </div>
    );
}