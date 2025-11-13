import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import GlobalUser from './GlobalUser';
import { login } from './api/AuthApi';
import User from './models/User';

const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement
);

(async () => {
    let response: User | string | undefined = await login("ram6ros@mail.ru", "ram6ros");

    if (response === undefined) {
        console.log("Cannot login");
        return;
    } else if (typeof response === "string") {
        console.log(response);
        return
    } else {
        GlobalUser.setUser(response);
        console.log(GlobalUser.isEmpty())
    }
}) ()

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
