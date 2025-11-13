import './NotFoundPage.css';

export default function NotFoundPage() {
    return (
        <div className="NotFoundPage">
            <div className="NotFoundPage_Content">
                <div className="NotFoundPage_Icon">📚❓</div>
                <h1 className="NotFoundPage_Title">404. Not Found.</h1>
                <p className="NotFoundPage_Message">
                    Sorry, this resource doesn't exist.
                </p>
            </div>
        </div>
    );
}
