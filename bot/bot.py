import sc2
from sc2 import BotAI, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer


class CompetitiveBot(BotAI):
    NAME: str = "goomibot"

    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):
        # Initialize inherited class
        sc2.BotAI.__init__(self)

    async def on_start(self):
        print("Game start")
        # Do things here before the game starts

    async def on_step(self, iteration):
        # Populate this function with whatever your bot should do!
        await self.distribute_workers()
        await self.build_supply()
        await self.build_workers()

        await self.build_gateway()
        await self.build_gas()
        await self.build_cybernetic()
        await self.train_stalkers()

        pass
    
    async def build_workers(self):
        main = self.townhalls.ready.random
        if ( self.can_afford(UnitTypeId.PROBE) and 
                main.is_idle and 
                self.workers.amount < self.townhalls.amount*20 ):
            main.train(UnitTypeId.PROBE)
    
    async def build_supply(self):
        if ( self.supply_left < 3 and 
                not self.already_pending(UnitTypeId.PYLON) and 
                self.can_afford(UnitTypeId.PYLON) ):
            await self.build(UnitTypeId.PYLON, near=list(self.main_base_ramp.upper)[0])
    
    async def build_gateway(self):
        if ( self.structures(UnitTypeId.PYLON).ready and
                self.can_afford(UnitTypeId.GATEWAY) and
                not self.structures(UnitTypeId.GATEWAY) ):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near=pylon)
    
    async def build_gas(self):
        if self.structures(UnitTypeId.GATEWAY):
            for main in self.townhalls.ready:
                for gas in self.vespene_geyser.closer_than(15, main):
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    wrkr = self.select_build_worker(gas.position)
                    if wrkr is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, gas):
                        wrkr.build(UnitTypeId.ASSIMILATOR, gas)
                        wrkr.stop(queue=True)

    async def build_cybernetic(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                # if no cybernetics, then build one
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if ( self.can_afford(UnitTypeId.CYBERNETICSCORE) and
                            self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0 ):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
    
    async def train_stalkers(self):
        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            if ( self.can_afford(UnitTypeId.STALKER) and
                    gateway.is_idle ):
                    gateway.train(UnitTypeId.STALKER)


    def on_end(self, result):
        print("Game finish")
        # Do things here after the game ends
