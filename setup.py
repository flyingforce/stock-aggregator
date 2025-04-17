from setuptools import setup, find_packages

setup(
    name="stock-aggregator",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=[
        "Flask==2.0.1",
        "Werkzeug==2.0.3",
        "redis==4.0.2",
        "requests>=2.31.0",
        "python-dotenv==0.19.0",
        "gunicorn==20.1.0",
        "Flask-SQLAlchemy==2.5.1",
        "PyYAML==6.0.1",
        "click==8.1.7",
        "yfinance>=0.2.36"
    ],
    entry_points={
        'console_scripts': [
            'stock-aggregator=stock_aggregator.app.cli:cli',
        ],
    },
    python_requires=">=3.9",
) 