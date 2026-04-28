"""A class representing a node in an AVL tree"""

class AVLNode(object):
	"""Constructor, you are allowed to add more fields. 
	
	@type key: int
	@param key: key of your node
	@type value: string
	@param value: data of your node
	"""
	def __init__(self, key, value):
		self.key = key
		self.value = value
		self.left = None
		self.right = None
		self.parent = None
		self.height = -1
		

	"""returns whether self is not a virtual node 

	@rtype: bool
	@returns: False if self is a virtual node, True otherwise.
	"""
	def is_real_node(self):
		return self.height != -1

	def get_height(self):
		return self.height

	def get_balance_factor(self):
		if not self.is_real_node():
			return 0
		return self.left.get_height() - self.right.get_height()


"""
A class implementing an AVL tree.
"""

class AVLTree(object):

	"""
	Constructor, you are allowed to add more fields.
	"""
	def __init__(self):
		self.root = None
		self._size = 0  
		self._max_node = None 

	def _get_virtual_node(self): 
		"""Returns a new, distinct virtual node instance."""
		return AVLNode(None, None)

	def _update_height(self, node):
		if node is None or not node.is_real_node():
			return -1
		node.height = 1 + max(node.left.get_height(), node.right.get_height())

	def _setup_leaf(self, node):
		"""Initializes a new real node with distinct virtual children and height 0."""
		node.left = self._get_virtual_node()
		node.right = self._get_virtual_node()
		# Virtual nodes must have their parent set correctly
		node.left.parent = node
		node.right.parent = node
		node.height = 0

	def _right_rotation(self, A):
		B = A.left
		A.left = B.right
		A.left.parent = A
		B.parent = A.parent
		if A.parent is None:
			self.root = B
		elif A == A.parent.right:
			A.parent.right = B
		else:
			A.parent.left = B
		B.right = A
		A.parent = B
		self._update_height(A)
		self._update_height(B)
		return B

	def _left_rotation(self, A):
		B = A.right
		A.right = B.left
		A.right.parent = A
		B.parent = A.parent
		if A.parent is None:
			self.root = B
		elif A == A.parent.left:
			A.parent.left = B
		else:
			A.parent.right = B
		B.left = A
		A.parent = B
		self._update_height(A)
		self._update_height(B)
		return B


	def rebalance_up(self, node): # Rebalance from node up to root
		# Start from parent of node	
		# at most tree hight iterations- log(n)
		curr = node.parent if (node.parent is not None) else node
		
		# Handle edge case where node is root
		if curr is None: 
			curr = node
			
		promotes_count = 0

		while curr is not None and curr.is_real_node():
			old_height = curr.height
			bf = curr.get_balance_factor()
			rotated = False

			# 1. Check for imbalance (BF > 1 or BF < -1)
			if abs(bf) > 1:
				# Perform Rotation (Case 2 or 3)
				if bf == -2:
					child_bf = curr.right.get_balance_factor()
					if child_bf <= 0:
						curr = self._left_rotation(curr)
					else:
						self._right_rotation(curr.right)
						curr = self._left_rotation(curr)

				elif bf == 2:
					child_bf = curr.left.get_balance_factor()
					if child_bf >= 0:
						curr = self._right_rotation(curr)
					else:
						self._left_rotation(curr.left)
						curr = self._right_rotation(curr)

				rotated = True

			# 2. Update height and count Promotes (Case 1)
			self._update_height(curr)

			if not rotated and curr.height > old_height:
				# Height changed (Promote Case 1) - count only if no rotation occurred
				promotes_count += 1
			
			curr = curr.parent

		return promotes_count


	"""searches for a node in the dictionary corresponding to the key (starting at the root)
        
	@type key: int
	@param key: a key to be searched
	@rtype: (AVLNode,int)
	@returns: a tuple (x,e) where x is the node corresponding to key (or None if not found),
	and e is the number of edges on the path between the starting node and ending node+1.
	"""
	def search(self, key): # starting at root 
		# at most tree height iterations- log(n)
		e = 0 
		curr = self.root
		while curr is not None and curr.is_real_node(): 
			e += 1
			if key == curr.key:
				return curr , e
			else:
				if key < curr.key:
					curr = curr.left
				else:
					curr = curr.right
		return None, e 


	"""searches for a node in the dictionary corresponding to the key, starting at the max
        
	@type key: int
	@param key: a key to be searched
	@rtype: (AVLNode,int)
	@returns: a tuple (x,e) where x is the node corresponding to key (or None if not found),
	and e is the number of edges on the path between the starting node and ending node+1.
	"""
	def finger_search(self, key):
		# at most tree height iterations up and down - log(n)
		if self.root is None:
			return None, 0
			
		e = 1
		curr = self._max_node 
		
		# Go UP until we find a node that might contain the key (curr.key <= key) or we hit root
		while curr.parent is not None and curr.key > key:
			curr = curr.parent
			e += 1
			
		# Now search DOWN as usual
		while curr is not None and curr.is_real_node():
			if key == curr.key:
				return curr , e
			else:
				e+=1
				if key < curr.key:
					curr = curr.left
				else:
					curr = curr.right
		return None, e 
	
	"""inserts a new node into the dictionary with corresponding key and value (starting at the root)

	@type key: int
	@pre: key currently does not appear in the dictionary
	@param key: key of item that is to be inserted to self
	@type val: string
	@param val: the value of the item
	@rtype: (AVLNode,int,int)
	@returns: a 3-tuple (x,e,h) where x is the new node,
	e is the number of edges on the path between the starting node and new node before rebalancing,
	and h is the number of PROMOTE cases during the AVL rebalancing
	"""
	def insert(self, key, val): 
		self._size += 1

		# Handle empty tree
		if self.root is None:
			self.root = AVLNode(key, val)
			self._setup_leaf(self.root)
			self._max_node = self.root
			return self.root, 0, 0 # e=0 (root), h=0

		 ##STEP 1 FIND PLACE
		e = 0 
		curr = self.root
		last = None
		while curr is not None and curr.is_real_node(): ##log(n)
			last = curr
			e += 1
			if key < curr.key:
				curr = curr.left
			else:
				curr = curr.right
			
	     ##STEP 2 INSERT NODE
		new_node = AVLNode(key, val)
		self._setup_leaf(new_node)
		new_node.parent = last

		if key < last.key:  
			last.left = new_node 
		else:
			last.right = new_node
			
		x = new_node
		
		if self._max_node is None or key > self._max_node.key:
			self._max_node = x
			
		## STEP 3 FIND AVL CRIMINALS ##log(n)
		h = self.rebalance_up(x)
		return (x, e, h)


	"""inserts a new node into the dictionary with corresponding key and value, starting at the max

	@type key: int
	@pre: key currently does not appear in the dictionary
	@param key: key of item that is to be inserted to self
	@type val: string
	@param val: the value of the item
	@rtype: (AVLNode,int,int)
	@returns: a 3-tuple (x,e,h) where x is the new node,
	e is the number of edges on the path between the starting node and new node before rebalancing,
	and h is the number of PROMOTE cases during the AVL rebalancing
	"""
	def finger_insert(self, key, val): 
		# at most tree height iterations up and down and up again to rebalance - log(n)
			# Handle empty tree
			if self.root is None:
				self._size += 1
				new_node = AVLNode(key, val)
				self._setup_leaf(new_node)
				self.root = new_node
				self._max_node = new_node
				return new_node, 1, 0 

			start_node = self._max_node 
			current = start_node
			edges_count = 0

			# A. Go up
			while current.parent is not None and key < current.key:
				current = current.parent
				edges_count += 1

			# B. Descend (standard search)
			parent_for_insert = None
			while current.is_real_node():
				parent_for_insert = current
				
				if key < current.key:
					if not current.left.is_real_node():
						break
					current = current.left
				else: # key > current.key
					if not current.right.is_real_node():
						break
					current = current.right
				edges_count += 1
			
			e = edges_count + 1

			# 2. Insert and link new node
			self._size += 1
			new_node = AVLNode(key, val)
			self._setup_leaf(new_node)

			new_node.parent = parent_for_insert
			if key < parent_for_insert.key:
				parent_for_insert.left = new_node
			else:
				parent_for_insert.right = new_node

			if self._max_node is None or key > self._max_node.key:
				self._max_node = new_node

			# 3. Rebalance and count 'promote' cases (h)
			h = self.rebalance_up(new_node)

			return new_node, e, h


	"""deletes node from the dictionary

	@type node: AVLNode
	@pre: node is a real pointer to a node in self
	"""

	def delete(self, node):
		# at most tree height iterations up for rebalancing - log(n)
		if node is None or not node.is_real_node():
			return

		self._size -= 1
		
		# Check if we are deleting the max node
		node_is_max = (node == self._max_node)
		
		# Case 1: Node is a leaf
		if not node.left.is_real_node() and not node.right.is_real_node():
			parent = node.parent
			if parent is None:
				self.root = None
			elif node == parent.left:
				parent.left = self._get_virtual_node()
				parent.left.parent = parent
			else:
				parent.right = self._get_virtual_node()
				parent.right.parent = parent
			
			if parent is not None:
				self.rebalance_up(node) 

		# Case 2: Node has two children
		elif node.left.is_real_node() and node.right.is_real_node():
			successor = node.right
			while successor.left.is_real_node():
				successor = successor.left
			
			# Swap content
			node.key = successor.key
			node.value = successor.value
			
			self._size += 1 # Restore size because recursive delete will decrease it
			self.delete(successor)
			# max_node check not needed here as we swapped data, we effectively deleted successor
			return 

		# Case 3: Node has one child
		else: 
			child = node.left if node.left.is_real_node() else node.right
			parent = node.parent
			
			child.parent = parent
			if parent is None:
				self.root = child
			elif node == parent.left:
				parent.left = child
			else:
				parent.right = child
			
			self.rebalance_up(child)

		# Update max_node if needed
		if node_is_max:
			if self.root is None:
				self._max_node = None
			else:
				curr = self.root
				while curr.right.is_real_node():
					curr = curr.right
				self._max_node = curr
		return

	"""joins self with item and another AVLTree

	@type tree2: AVLTree 
	@param tree2: a dictionary to be joined with self
	@type key: int 
	@param key: the key separting self and tree2
	@type val: string
	@param val: the value corresponding to key
	@pre: all keys in self are smaller than key and all keys in tree2 are larger than key,
	or the opposite way
	"""
	def join(self, tree2, key, val): 
			#go down gap between heights (h1-h2) at most then rebalance up height gap only (h1-h2) total (h1-h2)
			# Handle empty trees
			if (self.root is None or not self.root.is_real_node()) and \
			   (tree2.root is None or not tree2.root.is_real_node()):
				self.insert(key, val)
				return
			if self.root is None:
				self.root = tree2.root
				self._size = tree2.size() 
				self._max_node = tree2._max_node
				self.insert(key, val)
				return
			if tree2.root is None:
				self.insert(key, val)
				return

			new_node = AVLNode(key, val)
			self._setup_leaf(new_node)
			
			self._size += tree2.size() + 1 
			
			# Update max node
			if tree2._max_node and self._max_node:
				self._max_node = tree2._max_node if tree2._max_node.key > self._max_node.key else self._max_node
			elif tree2._max_node:
				self._max_node = tree2._max_node

			if self.root.key < key:
				T1_root = self.root
				T2_root = tree2.root
			else:
				T1_root = tree2.root
				T2_root = self.root

			h1 = T1_root.get_height() 
			h2 = T2_root.get_height()

			if h1 >= h2:
				# T1 is taller or equal. Go right in T1
				current = T1_root
				
				while current.is_real_node() and current.get_height() > h2:
					current = current.right
				
				y = current.parent 
				if y is None: 
					# new node becomes new root
					new_node.left = T1_root
					T1_root.parent = new_node
					new_node.right = T2_root
					T2_root.parent = new_node
					self.root = new_node
				else:
					y.right = new_node
					new_node.parent = y
					new_node.left = current
					current.parent = new_node
					new_node.right = T2_root
					T2_root.parent = new_node
					self.root = T1_root
					
				node_to_rebalance = new_node

			else:  # h2 > h1
				# T2 is taller. Go left in T2
				current = T2_root
				
				while current.is_real_node() and current.get_height() > h1:
					current = current.left
					
				y = current.parent
				
				if y is None:
					new_node.right = T2_root
					T2_root.parent = new_node
					new_node.left = T1_root
					T1_root.parent = new_node
					self.root = new_node
				else:
					y.left = new_node
					new_node.parent = y
					new_node.right = current
					current.parent = new_node
					new_node.left = T1_root
					T1_root.parent = new_node
					self.root = T2_root

				node_to_rebalance = new_node

			self._update_height(node_to_rebalance)
			self.rebalance_up(node_to_rebalance)
			return


	"""splits the dictionary at a given node

	@type node: AVLNode
	@pre: node is in self
	@param node: the node in the dictionary to be used for the split
	@rtype: (AVLTree, AVLTree)
	@returns: a tuple (left, right), where left is an AVLTree representing the keys in the 
	dictionary smaller than node.key, and right is an AVLTree representing the keys in the 
	dictionary larger than node.key.
	"""
	def split(self, node): # joins log(n) times, but height gap is at most 1, so each join is O(1) amortized, total O(log(n))
			left_tree = AVLTree()
			right_tree = AVLTree()

			# 1. Initial split - take the children subtrees
			if node.left.is_real_node():
				left_tree.root = node.left
				left_tree.root.parent = None

			if node.right.is_real_node():
				right_tree.root = node.right
				right_tree.root.parent = None

			current = node
			parent = current.parent
			
			while parent is not None:
				next_p = parent.parent
				
				# Is current the left child?
				if current == parent.left:
					# The parent and its right child belong to the RIGHT tree
					right_subtree = AVLTree()
					if parent.right.is_real_node():
						right_subtree.root = parent.right
						right_subtree.root.parent = None
					
					right_tree.join(right_subtree, parent.key, parent.value)
				
				else: # current == parent.right
					# The parent and its left child belong to the LEFT tree
					left_subtree = AVLTree()
					if parent.left.is_real_node():
						left_subtree.root = parent.left
						left_subtree.root.parent = None
					
					left_subtree.join(left_tree, parent.key, parent.value)
					left_tree = left_subtree

				current = parent
				parent = next_p

			# Update max nodes for returned trees
			if left_tree.root:
				curr = left_tree.root
				while curr.right.is_real_node():
					curr = curr.right
				left_tree._max_node = curr
				
			if right_tree.root:
				curr = right_tree.root
				while curr.right.is_real_node():
					curr = curr.right
				right_tree._max_node = curr
				
			return left_tree, right_tree

	
	"""returns an array representing dictionary 

	@rtype: list
	@returns: a sorted list according to key of touples (key, value) representing the data structure
	"""
	def avl_to_array(self): # goes over all nodes- O(n)
		result = []
		
		def _in_order_traversal(node):
			if node is not None and node.is_real_node():
				_in_order_traversal(node.left)
				result.append((node.key, node.value))
				_in_order_traversal(node.right)

		_in_order_traversal(self.root)
			
		return result


	"""returns the node with the maximal key in the dictionary

	@rtype: AVLNode
	@returns: the maximal node, None if the dictionary is empty
	"""
	def max_node(self):
		return self._max_node 

	"""returns the number of items in dictionary 

	@rtype: int
	@returns: the number of items in dictionary 
	"""
	def size(self):
		return self._size 


	"""returns the root of the tree representing the dictionary

	@rtype: AVLNode
	@returns: the root, None if the dictionary is empty
	"""
	def get_root(self):
		return self.root