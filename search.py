import requests

API_BASE_URL = 'http://openlibrary.org/search.json'

def book_search(book_title, author):
    """Handle search form submission and return results to mylibrary view function in app.py.
    
    Results format:
    [
        {
            "author_name": author,
            "first_publish_year": year,
            "number_of_pages_median": pages,
            "subject": subject,
            "title": title
        }, 
        ... 
    ]
    """

    response = search_entry(book_title, author)
   
    books = []

    # Format API response into list of dictionaries containing information on each book
    # Handle errors for when certain information is lacking from a search result.
    i = 0
    while i <= 50 :
        book = {}
        try:
            t = response.json()['docs'][i]['title']
        except (IndexError, KeyError):
            # Break loop when there's no more titles in API response (no more titles means no more books)
            break
        try:
            nums = [0,1,2,3,4]
            s = []
            for num in nums :
                subject = response.json()['docs'][i]['subject'][num]
                s.append(subject)
        except (IndexError, KeyError):
            pass
        try:
            n = str(response.json()['docs'][i]['number_of_pages_median'])
        except (IndexError, KeyError):
            n = "Not Found"
        a = response.json()['docs'][i]['author_name'][0]
        p = str(response.json()['docs'][i]['first_publish_year'])
        if bool(s) == False:
            s = "Not Found"

        book["title"] = t
        book["author_name"] = a
        book["first_publish_year"] = p
        book["number_of_pages_median"] = n
        book["subject"] = s
        
        books.append(book)
        i+=1
    return books

def search_entry(book_title, author):
    """Parse search entry submission and get response from API."""

    # search for book by title and author
    if len(book_title) > 0 and len(author) > 0:
        response = requests.get(API_BASE_URL, 
            params={'title': book_title, 'author': author})

    # search for book by title only
    elif len(book_title) > 0 and len(author) == 0:
        response = requests.get(API_BASE_URL, 
            params={'title': book_title})

    # search for book by author only
    elif len(book_title) == 0 and len(author) > 0:
        response = requests.get(API_BASE_URL, 
            params={'author': author})
    return response