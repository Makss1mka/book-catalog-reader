import User from "./models/User"

export default class GlobalUser {
    private static user: User | undefined = undefined;

    public static isEmpty(): boolean {
        return !this.user;
    }

    public static setUser(user: User) {
        this.user = user;
    }

    public static getUserId(): string | undefined {
        return this?.user?.id;
    }

    public static getUserName(): string | undefined {
        return this?.user?.username;
    }

    public static getUserEmail(): string | undefined {
        return this?.user?.email;
    }

    public static getUser(): User | undefined {
        return this?.user;
    }

    private GlobalUser() {}

}
