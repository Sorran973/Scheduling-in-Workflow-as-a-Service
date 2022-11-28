
def dfs(node, adj, dp, visited, pcp):
    visited[node] = True

    for i in range(0, len(adj[node])):
        j = adj[node][i]
        if not visited[adj[node][i]]:
            dfs(adj[node][i], adj, dp, visited, pcp)

        max_index = -1
        a = dp[node][j]
        if bool(adj[j]):
            max_index = dp[j].index(max(dp[j]))
            b = max(dp[j])
        else:
            b = 0

        if dp[node][j] < dp[node][j] + b:
            dp[node][j] += b
            # pcp[node][j] += pcp[j][max_index]
            pcp[node][j] = pcp[node][j] + [i for i in pcp[j][max_index] if i not in pcp[node][j]]



def addEdge(adj, u, v, dp, weight, pcp):
    adj[u].append(v)
    dp[u][v] = weight
    pcp[u][v] = [u, v]


def findLongestPath(adj, n):
    visited = [False] * (n)

    for i in range(n):
        if not visited[i]:
            dfs(i, adj, dp, visited, pcp)

    cp_length = 0
    cp = []

    for i in range(n):
        for j in range(n):
            if cp_length < dp[i][j]:
                cp_length = dp[i][j]
                cp = pcp[i][j]

    return cp_length, cp


if __name__ == "__main__":
    n = 4
    adj = [[] for i in range(n)]
    dp = [[0] * (n) for i in range(n)]
    pcp = [[[] * (n)] * (n) for i in range(n)]


    addEdge(adj, 0, 1, dp, 1, pcp)
    addEdge(adj, 0, 2, dp, 5, pcp)
    addEdge(adj, 2, 1, dp, 6, pcp)
    addEdge(adj, 1, 3, dp, 7, pcp)
    addEdge(adj, 2, 3, dp, 2, pcp)

    print(findLongestPath(adj, n))