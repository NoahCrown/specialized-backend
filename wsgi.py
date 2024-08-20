from waitress import serve
from server import app
import multiprocessing

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=10000, 
          threads=multiprocessing.cpu_count() * 2)