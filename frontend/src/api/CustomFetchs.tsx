import CommonResponse from "./CommonResponse";

export async function fetch_with_refresh<T>(url: string, options?: RequestInit): Promise<CommonResponse<T | string> | undefined> {
    let response: Response;

    try {
        response = await fetch(url, options);

        if (response.status === 401) {
            let refresh_token: string | null = "";
            if (typeof window !== 'undefined' && window.localStorage) {
                refresh_token = localStorage.getItem("refresh_token");
            }

            if (!refresh_token) {
                console.error("REFRESH: No refresh token found.");
                // TODO
                return undefined; 
            }
            
            const refreshResponse = await fetch("/api/user-service/refresh", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: refresh_token,
                })
            });

            if (refreshResponse.ok) {
                const refreshData = await refreshResponse.json();
                const access_token = refreshData.data.access_token;
                console.log(`REFRESH: new token ${access_token}`);
               
                response = await fetch(url, options);
            } else {
                console.log("REFRESH EXPIRED OR FAILED");
                // TODO
                return undefined;
            }
        }

        if (response.headers.get("Content-Type")?.includes('application/json')) {
            return await response.json();
        } else {
            return undefined;
        }

    } catch (error) {
        console.error("Fetch failed (network error):", error);
        return {
            "status": "exception",
            "data_type": "str",
            "data": "Oops, this is error on ours side",
        };
    }
}
