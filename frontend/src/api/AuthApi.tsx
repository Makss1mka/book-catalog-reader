import User from "../models/User";

export async function login(email: string, password: string): Promise<User | string | undefined> {
    let url = "/api/user-service/login";
    let response;
    
    try {
        response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    
        let json_result = (await response.json()).data;
        console.log(`LOGIN RES: ${json_result}`);

        let user: User = json_result.user_data;
        let access_token: string = json_result.access_token;
        let refresh_token: string = json_result.refresh_token;

        console.log(`LOGIN RES: user - ${user.id} ${user.username}`);
        console.log(`LOGIN RES: user - ${access_token}`);
        console.log(`LOGIN RES: user - ${refresh_token}`);

        if (typeof window !== 'undefined' && window.localStorage) {
            localStorage.setItem("refresh_token", refresh_token);
        }

        return user;
    } catch (error) {
        console.error("Error on fetch request:", error);
        
        if (response === undefined) return undefined;
    
        if (response.headers.get("Content-Type")?.includes('application/json')) {
            return (await response.json()).data;
        }

        return undefined
    }
} 

export async function register(username: string, email: string, password: string): Promise<User | string | undefined> {
    let url = "/api/user-service/register";
    let response;
    
    try {
        response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    
        let json_result = (await response.json()).data;
        console.log(`LOGIN RES: ${json_result}`);

        let user: User = json_result.user_data;
        let access_token: string = json_result.access_token;
        let refresh_token: string = json_result.refresh_token;

        console.log(`LOGIN RES: user - ${user}`);
        console.log(`LOGIN RES: user - ${access_token}`);
        console.log(`LOGIN RES: user - ${refresh_token}`);

        if (typeof window !== 'undefined' && window.localStorage) {
            localStorage.setItem("refresh_token", refresh_token);
        }

        return user;
    } catch (error) {
        console.error("Error on fetch request:", error);
        
        if (response === undefined) return undefined;
    
        if (response.headers.get("Content-Type")?.includes('application/json')) {
            return (await response.json()).data;
        }

        return undefined
    }
} 
