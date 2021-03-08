from datetime import datetime


def Articles():
    articles = [
        {
            'id': 1,
            'title': 'Article 1',
            'body': "Lorem ipsum, dolor sit amet consectetur adipisicing elit. Alias, beatae dignissimos tempora iste eos ducimus ipsam cupiditate, iusto reiciendis facilis repellat quasi blanditiis aut corporis et est unde deleniti aliquam?",
            'author': 'Raul Chakraborty',
            'create_date': datetime(2021, 2, 12)
        },
        {
            'id': 2,
            'title': 'Article 2',
            'body': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Alias, beatae dignissimos tempora iste eos ducimus ipsam cupiditate, iusto reiciendis facilis repellat quasi blanditiis aut corporis et est unde deleniti aliquam?',
            'author': 'Ishan Chakraborty',
            'create_date': datetime(2021, 2, 12)
        },
        {
            'id': 3,
            'title': 'Article 3',
            'body': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Alias, beatae dignissimos tempora iste eos ducimus ipsam cupiditate, iusto reiciendis facilis repellat quasi blanditiis aut corporis et est unde deleniti aliquam?',
            'author': 'Aadi Chakraborty',
            'create_date': datetime(2021, 2, 12)
        }
    ]

    return articles
