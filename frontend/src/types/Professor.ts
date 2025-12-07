export interface Professor {
    id: number;
    name: string;
    department: string;
    avgGrade: string;
    class: string;
    ratemyprofId?: number;         // RateMyProf ID
    overallRating?: number;        // RateMyProf overall rating (0-5)
    numRatings?: number;           // Number of ratings on RateMyProf
}