import pickle

if __name__ == '__main__':
    with open('papers.p', 'r') as f:
        data = pickle.load(f)

    print data