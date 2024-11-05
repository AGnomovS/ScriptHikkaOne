from .. import loader, utils
import asyncio
import re
import time
import random
from telethon.tl.types import Message, PeerUser
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
        self.report_answer = "Я играю честно, просто задрот."
        self.reported = False

    async def lesopilka_loop(self):
        while self.running:
            if self.sent_start_message == False:
                await self._client.send_message(6124218890, "лесопилка старт")
                self.sent_start_message = True
            if self.reported:
                await asyncio.sleep(10)  # Ждем, пока репорт не будет обработан и можно будет задротить
                continue
            delay = random.uniform(self.delay_min, self.delay_max)
            await asyncio.sleep(delay)

            async for message in self._client.iter_messages(6124218890, limit=1):
                if re.search(r"Вы начали рубить деревья|Вы успешно срубили дерево|вы слишком быстро пытаетесь рубить деревья", message.text, re.IGNORECASE):
                    await message.click(data=b"lesopilkasuccess")
                    self.count += 1
                elif re.search(r"начните заново работу на лесопилке", message.text, re.IGNORECASE):
                    await message.click(0)
                elif re.search(r"Вы уже находитесь на лесопилке", message.text, re.IGNORECASE):
                    await message.click(0)
                    await self._client.send_message(6124218890, "лесопилка старт")
                else:
                    await self._client.send_message(6124218890, "лесопилка старт")


    @loader.command()
    async def les(self, message: Message):
        """
        .les <задержка> - запустить/остановить лесопилку.
        .les <min-max> - запустить/остановить лесопилку с рандомной задержкой (можно использовать float, пример: 4.2-8.7).
        .les report <ответ> - установить ответ на репорт, который может поступить от администрации в целях проверки на автоматизацию
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
            await utils.answer(message, "Второй аргумент не был передан.")
            return
        
        if args.startswith("report "):
            self.report_answer = args.split("report ", maxsplit=1)[1]
            await utils.answer(message, f"Ответ на репорт установлен на:\n{self.report_answer}")
            return
        
        if "-" in args:
            try:
                self.delay_min, self.delay_max = map(float, args.split("-"))
            except ValueError:
                await utils.answer(message, "Укажите задержку в секундах (можно использовать float, например 4.2).")
                return
        else:
            try:
                self.delay_min = self.delay_max = float(args)
            except ValueError:
                await utils.answer(message, "Укажите задержку в секундах (можно использовать float, например 4.2).")
                return


        self.running = True
        self.start_time = time.time()

        asyncio.ensure_future(self.lesopilka_loop())
        await utils.answer(message, f"Лесопилка запущена с задержкой {self.delay_min}-{self.delay_max} секунд.\nОтвет на репорт: {self.report_answer}")


    @loader.unrestricted
    async def watcher(self, message: Message):
        if not self.running or not self.report_answer:
            return
        if not message.from_id or message.from_id != 6124218890:
            return
        if re.search(r"Поступило сообщение от администрации", message.text, re.IGNORECASE):
            self.reported = True
            await asyncio.sleep(random.uniform(2.5, 12.5))
            await utils.answer(message, f"репорт ({self.report_answer})")
            delay = random.uniform(80, 250)
            await asyncio.sleep(delay)
            self.reported = False
