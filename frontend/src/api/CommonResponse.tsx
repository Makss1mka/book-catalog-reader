
export default interface CommonResponse<T> {
    status: string;
    data_type: string;
    data: T;
}
