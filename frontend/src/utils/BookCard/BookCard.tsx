import ReactDOM from 'react-dom/client';
import { Book } from "../../models/Book"
import BookPage from "../../pages/BookPage/BookPage";
import './BookCard.css';

interface BookCardProps {
    book: Book;
}

export default function BookCard({ book }: BookCardProps) {
    const genres = (book.genres) 
        ? book.genres.join(", ") 
        : undefined;
    const rating = (book.total_rating !== undefined)
        ? Math.min(Math.max(Math.round(book.total_rating), 0), 5)
        : -1;
    const added_date = (book.added_date)
        ? new Date(book.added_date).toLocaleDateString()
        : undefined;

    const handleCardClicked = () => {
        let main = document.getElementById('main');

        if (!main) return;

        ReactDOM.createRoot(main).render(
            <BookPage book_id={ book.id } />
        );
    }

    console.log(rating);

    return (
        <div className="BookCard" onClick={ handleCardClicked }>
            <div className="BookCard_LeftSection">
                {
                    (book.cover_path === undefined) 
                    ? undefined 
                    : <img className="BookCard_cover" src={ book.cover_path } alt="Book cover"></img>
                }
            </div>
            <div className="BookCard_RigthSection">
                <label className="BookCard_Name">{book.title}</label>
                <p className="BookCard_Rating">
                    {
                        (rating === -1) 
                            ? undefined 
                            : <>
                                {'★'.repeat(rating)}
                                {'☆'.repeat(5 - rating)}
                                {` ${ book.total_rating }/5.0`}
                            </>
                    }
                </p>
                <p className="BookCard_Genres" title={genres}>{genres}</p>
                <p className="BookCard_Likes">{book.likes_count}</p>
                <p className="BookCard_AddedDate">{ added_date }</p>
            </div>
        </div>
    )
}
