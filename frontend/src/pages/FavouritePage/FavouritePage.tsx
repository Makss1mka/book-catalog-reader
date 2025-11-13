import { ErrorPage, ErrorPageWithoutMessage } from "../ErrorPage/ErrorPage";
import { getUserBookStatusedBooks } from "../../api/UserBookStatusesApi";
import { UserBookStatus } from "../../models/User";
import ReadingPage from "../ReadingPage/ReadingPage";
import BookPage from "../BookPage/BookPage";
import { useEffect, useState } from 'react';
import GlobalUser from '../../GlobalUser';
import ReactDOM from 'react-dom/client';
import './FavouritePage.css';


interface UserBookstatusCardProps {
    key: number;
    book: UserBookStatus;
}

export function UserBookstatusCard({ key, book }: UserBookstatusCardProps) {
    const handleOnBookPressed = () => {
        let main = document.getElementById('main');

        if (!main) return;

        ReactDOM.createRoot(main).render(
            <BookPage book_id={ book.book_id } />
        );
    }

    const handleContinueReadingPressed = () => {
        let main = document.getElementById('main');

        if (!main) return;

        ReactDOM.createRoot(main).render(
            <ReadingPage book_id={ book.book_id } initial_page={ book.end_page } />
        );
    }

    return (
        <div className="UserBookstatusCard" key={ key }>
            <div className="UserBookstatusCard_LeftPart" onClick={ handleOnBookPressed }>
                <p className="UserBookstatusCard_BookTitle">{ book.title }</p>
                <p className="UserBookstatusCard_AuthorName">{ book.author_name }</p>
            </div>
            <div className="UserBookstatusCard_RigthPart">
                <p className="UserBookstatusCard_EndPage">{ "You stopped on page " + book.end_page }</p>
                <button className="UserBookstatusCard_ContinueButton" onClick={ handleContinueReadingPressed }>Continue Reading...</button>
            </div>
        </div>
    );
}




export default function FavouritePage() {
    // LOVED BOOKS
    const [lovedBooks, setLovedBooks] = useState<UserBookStatus[]>([]);
    const [lovedBooksPageNum, setLovedBooksPageNum] = useState<number>(1);

    // ReAD BOOKS
    const [readBooks, setReadBooks] = useState<UserBookStatus[]>([]);
    const [readBooksPageNum, setReadBooksPageNum] = useState<number>(1);

    // READING BOOKS
    const [readingBooks, setReadingBooks] = useState<UserBookStatus[]>([]);
    const [readingBooksPageNum, setReadingBooksPageNum] = useState<number>(1);

    // DROP BOOKS
    const [dropBooks, setDropdBooks] = useState<UserBookStatus[]>([]);
    const [dropBooksPageNum, setDropBooksPageNum] = useState<number>(1);

    // COMMON
    const [currentStatus, setCurrentStatus] = useState<string>("LIKED");
    const [books, setBooks] = useState<UserBookStatus[]>([]);
    const [error, setError] = useState<string | null>(null);
    const pageSize = 10


    useEffect(() => {
        const loadBook = async (status: string, pageNum: number) => {
            const booksResp = await getUserBookStatusedBooks(status, pageNum, pageSize);

            if (booksResp === undefined || typeof booksResp.data === "string" || booksResp.data === null) {
                if (booksResp && typeof booksResp.data === "string") {
                    setError(booksResp.data);
                }
                return;
            }

            const loadedBooks = booksResp.data.books as UserBookStatus[];
            const newPageNum = booksResp.data.page_number + 1;

            switch (status) {
                case "LIKED":
                    setLovedBooks(loadedBooks);
                    setLovedBooksPageNum(newPageNum);
                    return;
                case "READ":
                    setReadBooks(loadedBooks);
                    setReadBooksPageNum(newPageNum);
                    return;
                case "READING":
                    setReadingBooks(loadedBooks);
                    setReadingBooksPageNum(newPageNum);
                    return;
                case "DROP":
                    setDropdBooks(loadedBooks);
                    setDropBooksPageNum(newPageNum);
                    return;
            }
            
        };

        loadBook("LIKED", lovedBooksPageNum);
        loadBook("READ", readBooksPageNum);
        loadBook("READING", readingBooksPageNum);
        loadBook("DROP", dropBooksPageNum);

        setBooks(lovedBooks);
    }, []); 


    const handleLovedPressed = () => {
        setBooks(lovedBooks);
        setCurrentStatus("LIKED");
    }

    const handleReadPressed = () => {
        setBooks(readBooks);
        setCurrentStatus("READ");
    }

    const handleReadingPressed = () => {
        setBooks(readingBooks);
        setCurrentStatus("READING");
    }

    const handleDropPressed = () => {
        setBooks(dropBooks);
        setCurrentStatus("DROP");
    }

    const handleBooksLoad = async () => {
        let pageNum;

        switch (currentStatus) {
            case "LIKED": pageNum = lovedBooksPageNum; break;
            case "DROP": pageNum = dropBooksPageNum; break;
            case "READ": pageNum = readBooksPageNum; break;
            case "READING": pageNum = readingBooksPageNum; break;
        }

        const booksResp = await getUserBookStatusedBooks(currentStatus, pageNum, pageSize);

        if (booksResp === undefined || typeof booksResp.data === "string" || booksResp.data === null) {
            if (booksResp && typeof booksResp.data === "string") {
                setError(booksResp.data);
            }
            return;
        }

        let newBooks = booksResp.data.books;
        let allBooks = [...(books || []), ...newBooks];

        setBooks(allBooks);
        
        switch (currentStatus) {
            case "LIKED": setLovedBooks(allBooks); break;
            case "DROP": setDropdBooks(allBooks); break;
            case "READ": setReadBooks(allBooks); break;
            case "READING": setReadingBooks(allBooks); break;
        }

        switch (currentStatus) {
            case "LIKED": setLovedBooksPageNum(prev => prev + 1); break;
            case "DROP": setDropBooksPageNum(prev => prev + 1); break;
            case "READ": setReadBooksPageNum(prev => prev + 1); break;
            case "READING": setReadingBooksPageNum(prev => prev + 1); break;
        }
    };




    if (GlobalUser.isEmpty()) {
        return <ErrorPage message="You are not authorized"/>
    }

    if (error) {
        return <ErrorPageWithoutMessage/>;
    }

    if (!books) {
        return <div className="FavouritePage">Loading...</div>;
    }

    return (
        <div className="FavouritePage">
            <div className="FavouritePage_SwitchButtons">
                <button className="FavouritePage_SwitchButton" onClick={ handleLovedPressed }>LOVED</button>
                <button className="FavouritePage_SwitchButton" onClick={ handleReadPressed }>READING</button>
                <button className="FavouritePage_SwitchButton" onClick={ handleReadingPressed }>ALREADY READ</button>
                <button className="FavouritePage_SwitchButton" onClick={ handleDropPressed }>DROP READING</button>
            </div>
            <div className="FavouritePage_BookCardsList">
                {books.map((book, index) => (
                    <UserBookstatusCard key={index} book={book} />
                ))}
            </div>
            <div className="CatalogPage_LoadButton_Outer">
                <button className="CatalogPage_LoadButton" onClick={ handleBooksLoad }>More...</button>
            </div>
        </div>
    );
}
