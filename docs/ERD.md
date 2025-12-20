erDiagram
    USER ||--|| USER_PROFILE : has
    USER ||--o{ REVIEW : writes
    USER ||--o{ REVIEW_LIKE : likes
    REVIEW ||--o{ REVIEW_LIKE : has
    USER ||--o{ WATCHLIST_ITEM : saves
    MOVIE ||--o{ WATCHLIST_ITEM : saved_in
    USER ||--o{ FOLLOW : follows_as_follower
    USER ||--o{ FOLLOW : follows_as_following
    MOVIE ||--o{ REVIEW : reviewed_on

    USER {
      int id PK
      string username "아이디(로그인용, unique)"
      string email "이메일(unique 권장)"
      string password "해시 저장"
      string real_name "이름"
      int age "나이"
      string gender "성별(M/F/OTHER 등)"
      datetime date_joined
      datetime last_login
      boolean is_active
    }

    USER_PROFILE {
      int id PK
      int user_id FK "USER.id (1:1)"
      string nickname "닉네임(unique)"
      string bio
      string avatar_url "이미지 URL 또는 media path"
      datetime created_at
      datetime updated_at
    }

    MOVIE {
      int id PK
      int tmdb_id "TMDB 영화 ID(unique)"
      string title
      string poster_path
      string backdrop_path
      date release_date
      float tmdb_vote_average
      datetime created_at
      datetime updated_at
    }

    REVIEW {
      int id PK
      int user_id FK "USER.id"
      int movie_id FK "MOVIE.id"
      string content "한줄평(200자 제한 권장)"
      int rating "1~5 필수"
      boolean watched "봤어요 체크(필수 True 권장)"
      int like_count "캐싱(기본 0)"
      datetime created_at
      datetime updated_at
    }

    REVIEW_LIKE {
      int id PK
      int user_id FK "USER.id"
      int review_id FK "REVIEW.id"
      datetime created_at
    }

    WATCHLIST_ITEM {
      int id PK
      int user_id FK "USER.id"
      int movie_id FK "MOVIE.id"
      string status "WANT|WATCHED"
      datetime created_at
      datetime updated_at
    }

    FOLLOW {
      int id PK
      int follower_id FK "USER.id"
      int following_id FK "USER.id"
      datetime created_at
    }
