import { addLikeToReview, deleteLikeFromReview, deleteReview } from "../../api/ReviewApi";
import { IconLikeEmpty, IconLikeFilled, IconTrashBin } from "../icons";
import { Review } from "../../models/Review";
import GlobalUser from "../../GlobalUser";
import { useState } from "react";
import "./ReviewCard.css";

interface ReviewCardProps {
    review: Review, 
    key: string
}

export default function ReviewCard({ review, key }: ReviewCardProps) {
    const [isLiked, setIsLiked] = useState<boolean>(review.is_liked_by_me);
    const [isDeleted, setIsDeleted] = useState<boolean>(false);
    const rating = (review.rating !== undefined)
        ? Math.min(Math.max(Math.round(review.rating), 0), 5)
        : -1;

    const handleLikeClick = async () => {
        if (!GlobalUser.getUser()) {
            console.log("Cannot handle like cause user is null", GlobalUser.getUser())
            return;
        }

        let response;
        if (isLiked) {
            response = await deleteLikeFromReview(review);

            if (response?.status === "success") {
                setIsLiked(false);
                review.likes_count--;
            } else {
                console.log(`Some error. ${response}.`);
            }
        } else {
            response = await await addLikeToReview(review);

            if (response?.status === "success") {
                setIsLiked(true);
                review.likes_count++;
            } else {
                console.log(`Some error. ${response}.`);
            }
        }
    };

    const handleDeleteClick = async () => {
        let author = GlobalUser.getUser()

        if (author === undefined || isDeleted) {
            console.log("Cannot handle delete pressing cause smth is null", author, isDeleted);
            return;
        }

        let response = await deleteReview(review);
        if (response?.status === "success") {
            setIsDeleted(true);
        } else {
            console.log(`Some error. ${response}.`);
        }
    }

    const isUserAuthor = () => {
        let globalUserId: string | undefined = GlobalUser.getUserId();
        
        if (globalUserId === undefined || globalUserId !== review.user_id) {
            return false;
        } else {
            return true;
        }
    }

    if (isDeleted) {
        return <></> 
    } else {
        return ( 
            <div className="ReviewCard" key={ key }>
                <div className="ReviewCard_UpperBlock">
                    <div className="ReviewCard_Author">{ review.user_name }</div>
                    {(isUserAuthor()) &&
                        <div className="ReviewCard_TrahsButton" onClick={ handleDeleteClick }>
                            <IconTrashBin className="ReviewCard_TrahsButton_Icon"/>
                        </div>
                    }
                </div>
                <div className="ReviewCard_Text">{ review.text }</div>
                <div className="ReviewCard_Rating">
                    {
                        (rating === -1)
                            ? undefined
                            : <>
                                {'★'.repeat(Math.round(rating))}
                                {'☆'.repeat(5 - Math.round(rating))}
                                {` ${ review.rating }/5.0`}
                            </>
                    }
                </div>
                <div className="ReviewCard_LikesBlock">
                    <div className="ReviewCard_Likes">{ review.likes_count }</div>
                    <button 
                        className="ReviewCard_LikeButton" 
                        onClick={handleLikeClick}
                    >
                        {isLiked 
                            ? <IconLikeFilled className="ReviewCard_LikeButtonIcon_Active" /> 
                            : <IconLikeEmpty className="ReviewCard_LikeButtonIcon_Inactive" />
                        }
                    </button>
                </div>
            </div>
        )
    }
}


