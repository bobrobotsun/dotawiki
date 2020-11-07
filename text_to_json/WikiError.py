

class editerror(RuntimeError):
    def __init__(self,lei='英雄',ku='主宰',reason='发生了未知错误，请检查后修正'):
        self.args=[lei,ku,reason]
    def get_error_info(self):
        return '《'+self.args[0]+'→'+self.args[1]+'》'+self.args[2]