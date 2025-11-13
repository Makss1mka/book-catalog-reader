import './CatalogPage.css';
import { useEffect, useState } from 'react';
import { getAllBooks } from "../../api/BooksApi";
import { Book } from "../../models/Book";
import BookCard from "../../utils/BookCard/BookCard";
import SearchBar from '../../utils/SearchBar/SearchBar';
import { ErrorPage } from '../ErrorPage/ErrorPage';

interface CatalogPageProps {
    genres?: string | null;
    keyWords?: string | null;
}

export default function CatalogPage({ keyWords = null, genres = null }: CatalogPageProps) {
    const [books, setBooks] = useState<Book[] | undefined>(undefined);
    const [error, setError] = useState<string | null>(null);
    const [pageNum, setPageNum] = useState<number>(1);
    const pageSize = 10

    useEffect(() => {
        const loadBook = async () => {
            const booksResp = await getAllBooks(keyWords, genres, pageNum, pageSize);

            if (booksResp === undefined || typeof booksResp.data === "string" || booksResp.data === null) {
                if (booksResp && typeof booksResp.data === "string") {
                    setError(booksResp.data);
                }
                return;
            }

            const loadedBooks = booksResp.data.books as Book[];
            const newPageNum = booksResp.data.page_number + 1;

            setBooks(loadedBooks);
            setPageNum(newPageNum);
        };

        loadBook();
    }, []); 

    const handleBooksLoad = async () => {
        const booksResp = await getAllBooks(keyWords, genres, pageNum, pageSize);

        if (booksResp === undefined || typeof booksResp.data === "string" || booksResp.data === null) {
            if (booksResp && typeof booksResp.data === "string") {
                setError(booksResp.data);
            }
            return;
        }

        let newBooks = booksResp.data.books;

        setBooks(prev => [...(prev || []), ...newBooks]);
        setPageNum(prev => prev + 1);
    };

    if (error) {
        return <ErrorPage message={ error }/>;
    }

    if (!books) {
        return <div className="CatalogPage">Loading...</div>;
    }

    return (
        <div className="CatalogPage">
            <SearchBar />
            <div className="CatalogPage_BookCardsList">
                {books.map((book, index) => (
                    <BookCard key={index} book={book} />
                ))}
            </div>
            <div className="CatalogPage_LoadButton_Outer">
                <button className="CatalogPage_LoadButton" onClick={ handleBooksLoad }>More...</button>
            </div>
        </div>
    );
}
