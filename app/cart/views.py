from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from products.models import Product
from .models import *
import datetime
from .extras import generate_order_id
from django.contrib import messages
from .forms import OrderForm
from django.http import JsonResponse, Http404, HttpResponseRedirect

# User = settings.AUTH_USER_MODEL
from django.contrib.auth import get_user_model


User = get_user_model()


# return user order object in cart if exists
def get_user_pending_cart(request):

    # get current logged-in user object otherwise return AnonymousUser
    # raise HTTP error code 404 if object exist
    user = get_object_or_404(User, username=request.user.username)

    order = Order.objects.filter(owner=user, is_ordered=False)
    if order.exists():
        return order[0]
    else:
        return 0


@login_required()
def add_item_to_cart(request):
    # add_item_to_cart(request, **kwargs):
    # ajax = request.GET.get('ajax', None)
    # if ajax:
    #     data = {'success': True}
    #     return JsonResponse(data)
    item_id = request.GET.get('item_id', None)
    username = request.user.username
    # create dictionary for JsonResponse data
    data = {'success': False}

    product = Product.objects.filter(id=item_id).first()
    user = get_object_or_404(User, username=username)

    if item_id and product:
        existing_cart = get_user_pending_cart(request)
        data['new_item'] = True
        if existing_cart:
            order_item = existing_cart.items.filter(product=product).first()
            if order_item:
                order_item.amount = order_item.amount + 1
                order_item.save()
                data['new_item'] = False
                data['success'] = True
                data['get_cart_qty'] = existing_cart.get_cart_qty()
                data['amount'] = str(order_item.amount)
            else:
                order_item, status = OrderItem.objects.get_or_create(product=product, owner=user)
                if status:
                    existing_cart.items.add(order_item)
                    existing_cart.save()
                    data['success'] = True
                    data['get_cart_qty'] = existing_cart.get_cart_qty()
        else:
            user_cart, status = Order.objects.get_or_create(owner=user, is_ordered=False)
            user_cart.ref_code = generate_order_id()
            if status:
                order_item = OrderItem.objects.create(product=product, owner=user)
                user_cart.items.add(order_item)
                user_cart.save()
                existing_cart = user_cart
                data['success'] = True
                data['get_cart_qty'] = '1'
                data['new_cart'] = True
                data['checkout_url'] = 'https://' + str(request.get_host()) + reverse('checkout')

        data['cart_total_value'] = str(existing_cart.get_cart_total())
        data['item_id'] = order_item.id
        if data['new_item']:
            data['product_url'] = 'https://' + str(request.get_host()) + str(product.get_absolute_url())
            data['product_thumbnail_url'] = 'https://' + str(request.get_host()) + str(product.thumbnail.url)
            data['product_subdepartment_name'] = product.subdepartment.name
            data['product_name'] = product.name
            data['product_price'] = str(product.price)
        # messages.info(request, "Product {} added to cart".format(product.name))
    return JsonResponse(data)


@login_required()
def delete_cart(request):

    data = {}

    existing_cart = get_user_pending_cart(request)

    delete_cart_items = OrderItem.objects.filter(owner_id=existing_cart.owner_id).delete()
    if delete_cart_items:
        delete_cart = existing_cart.delete()
        if delete_cart:
            data['success'] = delete_cart

    return JsonResponse(data)


@login_required()
def delete_item_from_cart(request):
    item_id = request.GET.get('item_id', None)

    # return if parameters not passed
    if item_id is None:
        return redirect('checkout')

    # create empty dictionary for JsonResponse data
    data = {}

    try:
        # check if new cart value and item_id are integers
        item_id = int(item_id)

    # render checkout site if request's argument isn't integer
    except ValueError as e:
        return HttpResponseRedirect(reverse_lazy('checkout'))  # todo check if need to return JsonReponse evertime

    item_to_delete = OrderItem.objects.filter(pk=item_id)
    if item_to_delete.exists():
        success = item_to_delete[0].delete()

        user = get_object_or_404(User, username=request.user.username)
        other_items = OrderItem.objects.filter(owner=user).first()
        existing_cart = get_user_pending_cart(request)
        # other_items = OrderItem.objects(order_id=existing_cart.id).first()

        if other_items:
            messages.info(request, "Item has been deleted")
            data['success'] = success
            data['cart_total_value'] = str(existing_cart.get_cart_total())
            data['get_cart_qty'] = str(existing_cart.get_cart_qty())
            data['item_qty'] = str()

        # remove cart if last product is deleted
        else:
            remove_cart = existing_cart.delete()
            data['remove_cart'] = remove_cart

    else:
        data['success'] = False
        data['ups'] = True
    return JsonResponse(data)


@login_required()
def calculate_item_in_cart(request):
    item_id = request.GET.get('item_id', None)
    new_cart_value = request.GET.get('cart_value', None)

    # return if parameters not passed
    if item_id is None and new_cart_value is None:
        return redirect('checkout')

    # create empty dictionary for JsonResponse data
    data = {}

    try:
        # check if new cart value and item_id are integers
        value = int(new_cart_value)
        item_id = int(item_id)

        # get current logged-in user order and order items objects in cart
        updated_item = OrderItem.objects.get(pk=item_id)

        # get current logged-in user order
        existing_cart = get_user_pending_cart(request)

    # render checkout site if request's arguments aren't integers
    # or if order or order item objects don't exist
    except (ValueError, Order.DoesNotExist, OrderItem.DoesNotExist) as e:
        return HttpResponseRedirect(reverse_lazy('checkout'))

    # check if value is in the right range
    if 0 < value <= MAX_ITEMS_IN_CART:
        try:
            success = OrderItem.objects.filter(pk=item_id).update(amount=value)
            data['success'] = success
            updated_item = OrderItem.objects.get(pk=item_id)

            # after successful update more data for JsonResponse
            if success:
                data['item_total_value'] = str(updated_item.get_item_total())
                data['cart_total_value'] = str(existing_cart.get_cart_total())

            # otherwise, raise an exception that cannot update record in database
            else:
                raise Http404('Cannot update OrderItem in database')
        except Http404 as error:
            return
    else:
        print('Incorrect product amount (max {} items)'.format(MAX_ITEMS_IN_CART))
        messages.error(request, 'Incorrect product amount (max {} items)'.format(MAX_ITEMS_IN_CART))
        data['success'] = False

    return JsonResponse(data)


@login_required()
def order_summary(request, **kwargs):
    existing_cart = get_user_pending_cart(request)
    context = {
        'cart': existing_cart
    }
    return render(request, 'cart/order_summary.html', context)


@login_required()
def checkout(request):
    order = get_user_pending_cart(request)
    items = 0 if isinstance(order, int) else order.get_cart_items()
    cart_item_form = 0 if isinstance(items, int) else OrderForm(initial={'amount': items[0].amount})

    if request.method == 'POST':
        cart_item_form = OrderForm(request.POST)

    context = {
        'order': order,
        'items': items,
        'cart_item_form': cart_item_form,
    }
    return render(request, 'cart/checkout.html', context)


@login_required()
def process_payment(request, cart_id):
    return redirect(reverse('cart:update_records',
                            kwargs={
                                'cart_id': cart_id,
                            })
                    )


@login_required()
def update_transaction_records(request, cart_id):
    order_to_purchase = Order.objects.filter(pk=cart_id).first()
    order_to_purchase.is_completed = True
    order_to_purchase.date_completed = datetime.datetime.now()
    order_to_purchase.save()

    order_items = order_to_purchase.items.all()
    order_items.update(is_completed=True, date_completed=datetime.datetime.now())

    return redirect(reverse('success'))


@login_required()
def success(request):
    return render(request, 'cart/success.html', {})



