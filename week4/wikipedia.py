import sys
import collections

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file, encoding="utf-8") as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()


    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()

    #ページIDを返す関数
    def get_page_id(self, title):
        for page_id, page_title in self.titles.items():
            if page_title == title:
                return page_id
            
        return None


    # Homework #1: Find the shortest path.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    #BFSを使って最短経路を探索する、キューを使う
    def find_shortest_path(self, start, goal):
        #startとgoalのページIDを取得
        start_id = self.get_page_id(start)
        goal_id = self.get_page_id(goal)

        if start_id == None or goal_id == None:
            print(start_id,"または",goal_id,"のどちらかが存在しません")
            return False
        
        queue = collections.deque() #キューの初期化
        visited = {}
        visited[start_id] = True #訪問済みのページIDとしてフラグを設定
        parent = {} #通過してきたページの親を記録
        queue.append(start_id) #スタートページをキューに追加

        #BFSのループ
        while queue:
            current_id = queue.popleft()
            if current_id == goal_id:
                #goalページに到達した場合、パスを復元
                path = []
                while current_id != start_id:
                    path.append(current_id)
                    current_id = parent[current_id]
                path.append(start_id)
                path.reverse() #パスを逆順にする
                titles = [self.titles[page_id] for page_id in path] #ページタイトルを取得
                print("->".join(titles))
                return
            
            #goalページに到達していない場合、隣接するページをキューに追加
            for neighbor_id in self.links[current_id]:
                if neighbor_id not in visited:
                    visited[neighbor_id] = True #フラグを設定
                    parent[neighbor_id] = current_id #親ページを記録
                    queue.append(neighbor_id) #隣接ノードをキューに追加

        print("No path found from", start, "to", goal)


    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        old_page_ranks = {} #更新前のページランク
        new_page_ranks = {} #更新後のページランク
        n = len(self.titles) #ページの総数
        for title_id in self.titles.keys():
            old_page_ranks[title_id] = 1.0/n #初期値として1.0/nを設定
            new_page_ranks[title_id] = 0.0 #初期値として0.0を設定
        damping_factor = 0.85 #ダンピングファクターの設定

        neighbor_node = {page_id: [] for page_id in self.titles.keys()} #自分がどの隣接ノードからリンクされているかを保持
        for page_id, links in self.links.items(): #リンクされているページを取得
            for link in links:
                neighbor_node[link].append(page_id)

        #ページランクの計算
        for _ in range(100):  # 最大100回の反復
            for page_id in self.titles.keys():
                new_page_ranks[page_id] = (1 - damping_factor) / n # 初期化
                # 自分をリンクしているページからのページランクを加算
                for neighbor in neighbor_node[page_id]: 
                    if len(self.links[neighbor]) > 0:
                        new_page_ranks[page_id] += damping_factor * (old_page_ranks[neighbor] / len(self.links[neighbor]))

            #収束判定とold_page_ranksの更新
            diff = max(abs(new_page_ranks[page_id] - old_page_ranks[page_id]) for page_id in self.titles.keys())
            old_page_ranks, new_page_ranks = new_page_ranks, old_page_ranks  # 更新前と更新後を入れ替え
            if diff < 1e-6:  # 十分に収束したら終了
                break

        top10_pages = sorted(old_page_ranks.items(), key=lambda x: x[1], reverse=True)[:10]  # ページランクの高い上位10ページを取得
        print("The most popular pages are:")
        for page_id, rank in top10_pages:
            print(f"{self.titles[page_id]}: {rank:.6f}")
        
        




    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pass


    # Helper function for Homework #3:
    # Please use this function to check if the found path is well formed.
    # 'path': An array of page IDs that stores the found path.
    #     path[0] is the start page. path[-1] is the goal page.
    #     path[0] -> path[1] -> ... -> path[-1] is the path from the start
    #     page to the goal page.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Example
    wikipedia.find_longest_titles()
    # Example
    wikipedia.find_most_linked_pages()
    # Homework #1
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # Homework #2
    wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")