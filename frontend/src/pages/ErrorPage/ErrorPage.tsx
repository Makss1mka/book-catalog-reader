import './ErrorPage.css';

interface ErrorPageProps {
    message: string;
}

export function ErrorPage({ message }: ErrorPageProps) {
    return (
        <div className="ErrorPage">
            <div className="ErrorPage_Content">
                <div className="ErrorPage_Icon">🚨 서버</div>
                <h1 className="ErrorPage_Title">Oupsss! Something goes wrong.</h1>
                <p className="ErrorPage_Message">
                    {message}
                </p>
                
                <div className="ErrorPage_Actions">
                    <button 
                        onClick={() => window.location.reload()} 
                        className="ErrorPage_Button ErrorPage_Button--Refresh"
                    >
                        Try to reload page...
                    </button>
                </div>
            </div>
        </div>
    );
}

export function ErrorPageWithoutMessage() {
    const defaultMessage = "An unexpected error occurred while processing your request. We are already working to resolve it.";
    
    return (
        <div className="ErrorPage">
            <div className="ErrorPage_Content">
                <div className="ErrorPage_Icon">🚨 서버</div>
                <h1 className="ErrorPage_Title">Oupsss! Something goes wrong.</h1>
                <p className="ErrorPage_Message">
                    {defaultMessage}
                </p>
                
                <div className="ErrorPage_Actions">
                    <button 
                        onClick={() => window.location.reload()} 
                        className="ErrorPage_Button ErrorPage_Button--Refresh"
                    >
                        Try to reload page...
                    </button>
                </div>
            </div>
        </div>
    );
}