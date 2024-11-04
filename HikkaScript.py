from .. import loader, utils
import asyncio
import re
import time
import random
from telethon.tl.types import Message
from telethon import Button

@loader.tds
class LesopilkaMod(loader.Module):
    """Автоматизирует работу с лесопилкой."""
    strings = {"name": "Lesopilka"}

    def __init__(self):
        self.running = False
        self.count = 0
        self.start_time = 0
        self.delay_min = None
        self.delay_max = None
        self.sent_start_message = False

    async def lesopilka_loop(self):
        while self.running:
            if self.sent_start_message == False:
                await self._client.send_message(6124218890, "лесопилка старт")
                self.sent_start_message = True

            delay = random.randint(self.delay_min, self.delay_max)
            await asyncio.sleep(delay)

            async for message in self._client.iter_messages(6124218890, limit=1):
                if re.search(r"Вы начали рубить деревья", message.text) or re.search(r"Вы успешно срубили дерево", message.text):
                    await message.click(data=b"lesopilkasuccess")
                    self.count += 1
                elif re.search(r"начните заново работу на лесопилке", message.text):
                    await message.click(0)
                elif re.search(r"Вы уже находитесь на лесопилке", message.text):
                    await message.click(0)
                    await self._client.send_message(6124218890, "лесопилка старт")
                else:
                    await self._client.send_message(6124218890, "лесопилка старт")


    @loader.command()
    async def les(self, message: Message):
        """
        .les <задержка> - запустить/остановить лесопилку.
        .les <min-max> - запустить/остановить лесопилку с рандомной задержкой.
        """
        args = utils.get_args_raw(message)

        if self.running:
            self.running = False
            self.sent_start_message = False
            elapsed_time = time.time() - self.start_time
            await utils.answer(message, f"Лесопилка остановлена.\nНажатий: {self.count}\nВремя работы: {utils.formatted_uptime()} ( {int(elapsed_time)} сек.)")
            self.count = 0
            self.start_time = 0
            return

        if not args:
            await utils.answer(message, "Укажите задержку в секундах.")
            return

        if "-" in args:
            try:
                self.delay_min, self.delay_max = map(int, args.split("-"))
            except ValueError:
                await utils.answer(message, "Неверный формат задержки. Пример: .les 5-10 (рандом от 5 до 10), .les 7 (каждые 7 секунд)")
                return
        else:
            try:
                self.delay_min = self.delay_max = int(args)
            except ValueError:
                await utils.answer(message, "Неверный формат задержки. Пример: .les 5-10 (рандом от 5 до 10), .les 7 (каждые 7 секунд)")
                return


        self.running = True
        self.start_time = time.time()

        asyncio.ensure_future(self.lesopilka_loop())
        await utils.answer(message, f"Лесопилка запущена с задержкой {self.delay_min}-{self.delay_max} секунд.")