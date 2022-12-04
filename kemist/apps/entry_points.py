import kemist.core as km
import kemist.apps as kapps


def kemist_db():
    pass


def kemist_db():
    parser = kapps.make_kemist_db_parser()
    args = parser.parse_args()

    km.set_verbose_logging(args.verbose)

    molecules = []
    storage_units = []
    if args.verb in ["create", "update"]:
        if args.interactive:
            kapps.confirm = kapps.interactive_confirm
            km.logger.debug(f"Using interactive matching")
        elif args.relaxed:
            kapps.confirm = kapps.relaxed_confirm
            km.logger.debug(f"Using relaxed matching")
        else:
            km.logger.debug(f"Using strict matching")

        if args.molecules is not None:
            molecules = kapps.load_molecules(args.molecules)
        if args.storage is not None:
            storage_units = kapps.load_storage_areas(args.storage)

    kemist_core = kapps.KemistDb()
    if args.verb == "create":
        kemist_core.create(args.database, molecules, storage_units, args.complete, args.make_default)
    elif args.verb == "set":
        kemist_core.set_default(args.database)
    elif args.verb == "list":
        kemist_core.list_databases()
    elif args.verb == "export":
        kemist_core.export(args.database, args.output)
    elif args.verb == "update":
        kemist_core.update(args.database, molecules, storage_units, args.complete)


if __name__ == "__main__":
    kemist_db()
