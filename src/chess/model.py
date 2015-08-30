import unittest
from sqlalchemy.dialects import postgresql

PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = PIECES = range(6)

class Color(object):
    def __init__(self, shortname, firstrow, lastrow, advance):
        self.shortname = shortname
        self.firstrow = firstrow
        self.lastrow = lastrow
        self.advance = advance
        
    def opposite(self):
        return opposite_color(self)
        
PIECES_SHORTNAMES = {PAWN : "P", KNIGHT: "N", BISHOP: "B", ROOK: "R", QUEEN: "Q", KING : "K"}
PIECES_FROM_CHAR = dict((v, k) for k,v in PIECES_SHORTNAMES.iteritems())   
    
#BLACK, WHITE = COLORS = range(2)
#COLOR_SHORTNAMES = {BLACK:"b", WHITE:"w"}
BLACK = Color("b", 7, 0, -1)
WHITE = Color("w", 0, 7, 1)
def opposite_color(color):
    return BLACK if color == WHITE else WHITE

class Piece(object):
    def __init__(self, type, color):
        self.type = type
        self.color = color
    def __eq__(self, other):
        return (self.type == other.type and 
                self.color == other.color) 
    def __hash__(self):
        return hash((self.type, self.color))
                
    def __repr__(self):
        return self.color.shortname + PIECES_SHORTNAMES[self.type]
 
class SquareNotEmpty(Exception):
    pass

class SquareEmpty(Exception):
    pass

class IncorrectPosition(Exception):
    pass

class Board(object):
    def __init__(self):
        self.squares = [[None] * 8 for _ in range(8)]
    
    def algebraic_to_idx(self, algebraic_str):
        """ 'e', '4' => (4, 3) """ 
        pass 
    
    def algebraic_file_to_idx(self, file):
        return "abcdefgh".index(file) 
    
    def algebraic_rank_to_idx(self, rank):
        return "01234567".index(file)
    
    def add(self, position, piece):
        pos =  Position.from_any(position)
        if self.squares[pos.y][pos.x] is not None:
            raise SquareNotEmpty()
        if pos.y == piece.color.lastrow and piece.type == PAWN:
            raise IncorrectPosition("pawn on last row")
        self.squares[pos.y][pos.x] = piece
        
    def remove(self, position):
        if self[position] is None:
            raise SquareEmpty()
        self[position] = None
    
    def get(self, position):
        return self[position]

    def __getitem__(self, postype):
        pos =  Position.from_any(postype)
        return self.squares[pos.y][pos.x]

    def __setitem__(self, postype, value):
        pos =  Position.from_any(postype)
        self.squares[pos.y][pos.x] = value

    def iterpieces(self):
        for y in range(8):
            for x in range(8):
                if self.squares[y][x] is not None:
                    yield (Position(x, y), self.squares[y][x])
                    
    @classmethod
    def setup(cls, pos_pieces):
        board = cls()
        for pos, piece in pos_pieces.iteritems():
            board.add(pos, piece)
        return board
    
    def __repr__(self):
        row_reprs = []
        row_reprs.append("   " + "".join([str(c) + " " for c in "abcdefgh"]))
        for i, row in enumerate(self.squares):
            row_reprs.append(str(i+1) + "  " + "".join([str(p) if p is not None else "  " for p in row]))
        return "\n".join(reversed(row_reprs))

class ChessNotationSyntaxError(Exception):
    pass
class InvalidPosition(Exception):
    pass

class Position(object):
    COLS = "abcdefgh"
    ROWS = "12345678"
    def __init__(self, x, y):
        if x < 0 or  x > 7:
            raise InvalidPosition()
        if y < 0 or  y > 7:
            raise InvalidPosition()
        self.x = x
        self.y = y
        
    @staticmethod
    def algebraic_file_to_idx(file):
        idx = Position.COLS.index(file)
        if idx is -1:
            raise ChessNotationSyntaxError("File: '%s'" % (file))
        return idx
    
    @staticmethod
    def algebraic_rank_to_idx(rank):
        idx = Position.ROWS.index(rank)
        if idx is -1:
            raise ChessNotationSyntaxError("Rank: '%s'" % (rank))
        return idx
    
    @staticmethod
    def from_str(algebraic_str):
        """ e.g. 'e4' => Position """ 
        col, row = algebraic_str
        return Position(Position.algebraic_file_to_idx(col), Position.algebraic_rank_to_idx(row))
    
    @staticmethod
    def from_any(pos):
        if type(pos) is str:
            return Position.from_str(pos)
        if type(pos) is tuple:
            return Position.from_str(*pos)
        if isinstance(pos, Position):
            return pos
        raise Exception("Unknown position type")
    
    def __repr__(self):
        return Position.COLS[self.x] + Position.ROWS[self.y]

    def __eq__(self, other):
        return (self.x == other.x and 
                self.y == other.y) 
    def __hash__(self):
        return hash((self.x, self.y))
    
class RelPosition(Position):
    def __init__(self, x, y, color):
        super(RelPosition, self).__init__(x, y)
        self.color = color
        
    def lastrow(self):
        return self.y == self.color.lastrow

    def prevlastrow(self):
        return self.y == self.color.lastrow - self.color.advance
        
    def firstrow(self):
        return self.y == self.color.firstrow

    def secondrow(self):
        return self.y == self.color.firstrow + self.color.advance
        
    def advance(self, advance=0, sideway=0):    
        return RelPosition(self.x + self.color.advance * sideway, self.y + self.color.advance * advance, self.color)

class Game(object):
    def __init__(self, board=None, turn=WHITE, rules=None):
        self.board = board or Board()
        self.turn = turn
        self.rules = rules

SIMPLE, TAKE, ROQUE, PROMOTE, EN_PASSANT = MOVE_TYPES = range(5)
# what about taking as a pawn on last row? is thie promote?

class BoardChange(object):
    pass


class Move(object):
    def __init__(self, pos1, pos2, take=[], takepos=None, promote=[], moves=[]):
        self.pos1 = pos1
        self.pos2 = pos2
        self.take = take
        self.takepos = takepos
        self.promote = promote
        self.moves = moves

    @staticmethod
    def from_str(str, board):
        if len(str) == 4:
            return Move(Position.from_str(str[:2]), Position.from_str(str[2:]))
        elif len(str) == 5 and str[2] == 'x':
            pass
        elif len(str) == 6 and str[4] == '=':
            if str[5] not in PIECES_FROM_CHAR:
                raise ChessNotationSyntaxError("no such piece: " + str[5])
            return Move(Position.from_str(str[:2]), Position.from_str(str[2:4]), promote=PIECES_FROM_CHAR[str[5]])
        
    def __repr__(self):
        return "%s%s" % (self.pos1, self.pos2)

    def __eq__(self, other):
        return (self.pos1 == other.pos1 and
                self.pos2 == other.pos2 and
                self.promote == other.promote)

    def __hash__(self):
        return hash((self.pos1, self.pos2))


class Rules(object):
    def addsimplemove(self, pos, board, dx, dy, moves, move=False, take=False, promote=False):
        try:
            square = pos.advance(dy, dx)
        except InvalidPosition:
            return
        piece = board[square]
        if piece is None and move:
            if not promote:
                moves.append(Move(pos, square))
            else:
                for p in set([ROOK, QUEEN, KNIGHT, BISHOP]):
                    moves.append(Move(pos, square, promote=p))
        if piece is not None and take and piece.color == board[pos].color.opposite():
            if not promote:
                moves.append(Move(pos, square, take=piece))
            else:
                for p in set([ROOK, QUEEN, KNIGHT, BISHOP]):
                    moves.append(Move(pos, square, take=piece, promote=p))
                
    def pawnmoves(self, pos, board, pawn):
        moves = []
        self.addsimplemove(pos, board, 0, 1, moves, move=True, promote=pos.prevlastrow())
        if pos.secondrow():
            self.addsimplemove(pos, board, 0, 2, moves, move=True)
        self.addsimplemove(pos, board, 1, 1, moves, take=True, promote=pos.prevlastrow())
        self.addsimplemove(pos, board, -1, 1, moves, take=True, promote=pos.prevlastrow())
        return moves
    
    def genmoves(self, board, player):
        moves = []
        for pos, piece in board.iterpieces():
            if piece.color == player:
                relpos = RelPosition(pos.x, pos.y, piece.color)
                if piece.type == PAWN:
                    moves += self.pawnmoves(relpos, board, piece)
        return moves
    
    def is_allowed(self, board, move, player):
        return move in self.genmoves(board, player)
    
    @staticmethod
    def allowed(boarddef, movestr):
        board= Board.setup(boarddef)
        move = Move.from_str(movestr, board)
        rules = Rules()
        return move in rules.genmoves(board, board[move.pos1].color)
        
class UnitTests(unittest.TestCase):
    def test_Board_AddPieceOnEmptySquare_GetReturnsPiece(self):
        b = Board()
        b.add("e4", Piece(PAWN, WHITE))
        
        self.assertEquals(b.get("e4"), Piece(PAWN, WHITE))

    def test_Board_AddPieceOnFullSquare_RaisesSquareNotEmptyException(self):
        b = Board()
        b.add("e4", Piece(PAWN, WHITE))
        
        with self.assertRaises(SquareNotEmpty):
            b.add("e4", Piece(PAWN, WHITE))

    def test_Board_AddPieceOnFullSquareAndRemove_GetReturnsNone(self):
        b = Board()
        b.add("e4", Piece(PAWN, WHITE))
        b.remove("e4")
        
        self.assertIs(b.get("e4"), None)

    def test_Board_AddPawnOnLastRow_RaisesException(self):
        b = Board()
        
        with self.assertRaises(IncorrectPosition):
            b.add("e8", Piece(PAWN, WHITE))
        with self.assertRaises(IncorrectPosition):
            b.add("e1", Piece(PAWN, BLACK))

    def test_Board_RemovePieceFromEmptySquare_RaisesException(self):
        b = Board()
        
        with self.assertRaises(SquareEmpty):
            b.remove("e4")

    def test_PawnAdvances_WhitePawnOnE2_IsAllowedToAdvanceOneSquare(self):
        assert Rules.allowed({"e2" : Piece(PAWN, WHITE)}, "e2e3")

    def test_PawnCaptures_WhitePawnOnE2_CannotGotoD3(self):
        assert not Rules.allowed({"e2" : Piece(PAWN, WHITE)}, "e2d3")

    def test_PawnAdvances_WhitePawnOnE2_IsAllowedToAdvanceTwoSquares(self):
        assert Rules.allowed({"e2" : Piece(PAWN, WHITE)}, "e2e4")
        
    def test_PawnAdvances_WhitePawnOnD2_IsAllowedToAdvanceTwoSquares(self):
        assert Rules.allowed({"d2" : Piece(PAWN, WHITE)},
                              "d2d4")
    def test_PawnAdvances_WhitePawnOnF6_CanNotAdvance2Squares(self):
        assert not Rules.allowed({"f6" : Piece(PAWN, BLACK)}, "f6f8")

    def test_PawnAdvances_WhitePawnOnF3WithWhitePieceInFront_CanNotAdvance(self):
        assert not Rules.allowed({"f3" : Piece(PAWN, WHITE),
                                  "f4" : Piece(ROOK, WHITE),
                                  }, "f3f4")

    def test_PawnAdvances_WhitePawnOnF3WithBlackPieceInFront_CanNotAdvance(self):
        assert not Rules.allowed({"f3" : Piece(PAWN, WHITE),
                                  "f4" : Piece(ROOK, BLACK),
                                  }, "f3f4")

    def test_PawnAdvances_WhitePawnOnF7_CanNotAdvance(self):
        assert not Rules.allowed({"f7" : Piece(PAWN, WHITE)}, "f7f8")
        
    def test_PawnAdvances_BlackPawnOnF1_CanNotAdvance(self):
        assert not Rules.allowed({"f2" : Piece(PAWN, BLACK)}, "f2f1")
        
                
    def test_PawnAdvances_BlackPawnOnE2_IsNotAllowedToAdvance(self):
        assert not Rules.allowed({"e2" : Piece(PAWN, BLACK)}, "e2e3")
        
    def test_PawnAdvances_BlackPawnOnE7_CanAdvance1Square(self):
        assert Rules.allowed({"e7" : Piece(PAWN, BLACK)}, "e7e6")
        
    def test_PawnAdvances_BlackPawnOnE7_CanAdvance2Square(self):
        assert Rules.allowed({"e7" : Piece(PAWN, BLACK)}, "e7e5")
        
    def test_PawnAdvances_BlackPawnOnC4_CanAdvance1Square(self):
        assert Rules.allowed({"c4" : Piece(PAWN, BLACK)}, "c4c3")
        
    def test_PawnAdvances_BlackPawnOnC4_CanNotAdvance2Square(self):
        assert not Rules.allowed({"c4" : Piece(PAWN, BLACK)}, "c4c2")
        
    def test_PawnCaptures_WhitePawnOnE2WithBlackPawnOnD3_IsAllowedToTakeD3(self):
        assert Rules.allowed({"e2" : Piece(PAWN, WHITE),
                              "d3" : Piece(PAWN, BLACK),}, "e2d3")

    def test_PawnCaptures_WhitePawnOnE2_CantGoToD3IfThereIsNoPieceThere(self):
        assert not Rules.allowed({"e2" : Piece(PAWN, WHITE)}, "e2d3")

    def test_PawnCaptures_WhitePawnOnE2WithWhitePawnOnD3_IsNotAllowedItsOwnPawn(self):
        assert not Rules.allowed({"e2" : Piece(PAWN, WHITE),
                                  "d3" : Piece(PAWN, WHITE),}, "e2d3")

    def test_PawnPromote_WhitePawnOnE7_IsAllowedToPromoteOnE8(self):
        assert Rules.allowed({"e7" : Piece(PAWN, WHITE)}, "e7e8=Q")
        assert Rules.allowed({"e7" : Piece(PAWN, WHITE)}, "e7e8=R")
        assert Rules.allowed({"e7" : Piece(PAWN, WHITE)}, "e7e8=B")
        assert Rules.allowed({"e7" : Piece(PAWN, WHITE)}, "e7e8=N")
        assert not Rules.allowed({"e7" : Piece(PAWN, WHITE)}, "e7e8=P")
        assert not Rules.allowed({"e7" : Piece(PAWN, WHITE)}, "e7e8=K")

    def test_PawnPromote_WhitePawnOnE7WithPieceOnE8_CannotPromoteOnE8(self):
        assert not Rules.allowed({"e7" : Piece(PAWN, WHITE),
                                  "e8" : Piece(KNIGHT, WHITE)}, "e7e8=Q")
        assert not Rules.allowed({"e7" : Piece(PAWN, WHITE),
                                  "e8" : Piece(KNIGHT, BLACK)}, "e7e8=Q")

    def test_PawnPromote_WhitePawnOnE7AndBlackPieceOnD8_IsAllowedToTakeAndPromoteOnD8(self):
        assert Rules.allowed({"e7" : Piece(PAWN, WHITE),
                              "d8" : Piece(KNIGHT, BLACK)}, "e7d8=Q")
        
    def test_PawnPromote_WhitePawnOnE7AndWhitePieceOnD8_IsNotAllowedToTakeAndPromoteOnD8(self):
        assert not Rules.allowed({"e7" : Piece(PAWN, WHITE),
                                  "d8" : Piece(KNIGHT, WHITE)}, "e7d8=Q")


if __name__ == "__main__":
    unittest.main()
    
        